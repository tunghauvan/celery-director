import logging
from pathlib import Path
from celery import Task as _Task
from celery.signals import task_prerun, task_postrun
from celery.utils.log import get_task_logger

from director.extensions import cel, db, cel_minio
from director.models import StatusType
from director.models.workflows import Workflow
from director.models.tasks import Task

logger = get_task_logger(__name__)

@task_prerun.connect
def director_prerun(task_id, task, *args, **kwargs):
    if task.name.startswith("director.tasks"):
        return

    with cel.app.app_context():
        task = Task.query.filter_by(id=task_id).first()
        task.status = StatusType.progress
        task.save()

@task_postrun.connect
def close_session(*args, **kwargs):
    db.session.remove()

class BaseTask(_Task):
    def __call__(self, *args, **kwargs):
        task_id = self.request.id
        self.logger = self.setup_logger(task_id)
        return super(BaseTask, self).__call__(*args, **kwargs)
    
    def setup_logger(self, task_id):
        log_dir = cel.app.config["CELERYD_LOG_DIR"] = "logs"
        # Create log directory if it does not exist
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        log_filename = f"{log_dir}/{task_id}.log"
        task_logger = logging.getLogger(task_id)
        task_logger.setLevel(logging.INFO)

        # Check if the logger already has handlers
        if not task_logger.handlers:
            # Create file handler which logs even debug messages
            fh = logging.FileHandler(log_filename)
            fh.setLevel(logging.INFO)

            # Create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)

            # Add the handlers to the logger
            task_logger.addHandler(fh)
        
        return task_logger
    
    def send_log_to_minio(self, task_id):
        if not cel_minio:
            return
        log_dir = cel.app.config["CELERYD_LOG_DIR"]
        log_filename = f"{log_dir}/{task_id}.log"
        object_name = f"logs/{task_id}.log"
        cel_minio.upload(log_filename, object_name)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        task_logger = self.setup_logger(task_id)
        task_logger.error(f"Task {task_id} failed with exception: {exc}")
        task_logger.error(str(einfo.traceback))

        task = Task.query.filter_by(id=task_id).first()
        task.status = StatusType.error
        task.result = {"exception": str(exc), "traceback": einfo.traceback}
        task.workflow.status = StatusType.error
        task.save()
        task_logger.info(f"Task {task_id} is now in error")

        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)
        self.send_log_to_minio(task_id)

    def on_success(self, retval, task_id, args, kwargs):
        task_logger = self.setup_logger(task_id)
        task_logger.info(f"Task {task_id} completed successfully with result: {retval}")

        task = Task.query.filter_by(id=task_id).first()
        task.status = StatusType.success
        task.result = retval
        task.save()

        task_logger.info(f"Task {task_id} is now in success")
        super(BaseTask, self).on_success(retval, task_id, args, kwargs)
        self.send_log_to_minio(task_id)