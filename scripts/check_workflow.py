import argparse
import time
from flask import current_app as app
from director import create_app
from director.models.workflows import Workflow
from director.models import StatusType
from director.builder import WorkflowBuilder
from director import db  # Import the db object


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Check a workflow")
    # parser.add_argument("uuid", type=str, help="The UUID of the workflow run")
    # args = parser.parse_args()

    app = create_app()
    project = "example"
    name = "ETL"
    payload = {}
    comment = None

    # Create the workflow in DB
    obj = Workflow(project=project, name=name, payload=payload, comment=comment)
    obj.save()

    # Build the workflow and execute it
    data = obj.to_dict()
    workflow = WorkflowBuilder(obj.id)
    workflow.run()

    while True:
        workflow_run = Workflow.query.filter_by(id=obj.id).first()
        if workflow_run.status != StatusType.pending and workflow_run.status != StatusType.progress:
            print(f"Workflow status: {workflow_run.status}")
            break
        db.session.refresh(workflow_run)  # Refresh the object from the database
        # print(workflow_run.__dict__)
        time.sleep(0.5)