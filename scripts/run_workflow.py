from director import create_app
import time

import pytz
from flask import abort, jsonify, request
from flask import current_app as app

from director import db  # Import the db object
from director.api import validate
from director.builder import WorkflowBuilder
from director.exceptions import WorkflowNotFound
from director.extensions import cel_workflows
from director.models import StatusType
from director.models.workflows import Workflow


def _execute_workflow(project, name, payload={}, comment=None):
    fullname = f"{project}.{name}"

    # Check if the workflow exists
    try:
        wf = cel_workflows.get_by_name(fullname)
        if "schema" in wf:
            validate(payload, wf["schema"])
    except WorkflowNotFound:
        abort(404, f"Workflow {fullname} not found")

    # Create the workflow in DB
    obj = Workflow(project=project, name=name, payload=payload, comment=comment)
    obj.save()

    # Build the workflow and execute it
    data = obj.to_dict()
    workflow = WorkflowBuilder(obj.id)
    workflow.run()

    app.logger.info(f"Workflow sent : {workflow.canvas}")
    return obj.to_dict(), workflow


def _list_workflows():
    for fullname, definition in sorted(cel_workflows.workflows.items()):
        print(f"{fullname} : {definition}")


def _create_workflow(project, name, payload={}, comment=None):
    fullname = f"{project}.{name}"

    # Check if the workflow exists
    try:
        wf = cel_workflows.get_by_name(fullname)
        if "schema" in wf:
            validate(payload, wf["schema"])
    except WorkflowNotFound:
        print(f"Workflow {fullname} not found")

    cel_workflows.add_workflow(fullname, payload)

    # Create the workflow in DB
    obj = Workflow(project=project, name=name, payload=payload, comment=comment)
    obj.save()

    return obj.to_dict()


def _update_workflow(project, name, payload={}, comment=None):
    fullname = f"{project}.{name}"

    # Check if the workflow exists
    try:
        wf = cel_workflows.get_by_name(fullname)
        if "schema" in wf:
            validate(payload, wf["schema"])
    except WorkflowNotFound:
        print(f"Workflow {fullname} not found")

    cel_workflows.update_workflow(fullname, payload)

    # Create the workflow in DB
    obj = Workflow(project=project, name=name, payload=payload, comment=comment)
    obj.save()

    return obj.to_dict()

def _wait_for_workflow_run(workflow_run_id):
    while True:
        workflow_run = Workflow.query.filter_by(id=workflow_run_id).first()
        db.session.refresh(workflow_run)
        # print(workflow_run.__dict__)
        if workflow_run.status != StatusType.pending and workflow_run.status != StatusType.progress:
            print(f"Workflow status: {workflow_run.status}")
            return workflow_run
        time.sleep(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run a workflow")
    # args wait for the workflow to finish
    parser.add_argument("--wait", action="store_true", help="Wait for the workflow to finish")
    args = parser.parse_args()
    
    app = create_app()
    workflow_run, _ = _execute_workflow(
        "example",
        "ETL",
        {},
        "example",
    )
    print(workflow_run['id'])
    if args.wait:
        _wait_for_workflow_run(workflow_run['id'])
    