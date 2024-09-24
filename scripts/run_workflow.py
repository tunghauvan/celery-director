from director import create_app
from datetime import datetime, timedelta
from distutils.util import strtobool

import pytz
from flask import abort, jsonify, request
from flask import current_app as app

from director.api import validate
from director.builder import WorkflowBuilder
from director.exceptions import WorkflowNotFound
from director.extensions import cel_workflows
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
    
if __name__ == '__main__':
    app = create_app()
    _create_workflow('example', 'TEST', {'tasks': ['EXTRACT', 'TRANSFORM', 'LOAD']})
    print('-'*80)
    _list_workflows()
    _update_workflow('example', 'TEST', {'tasks': ['EXTRACT', 'TRANSFORM', 'LOAD', 'TEST']})
    print('-'*80)
    _list_workflows()
    # print(
    #     _execute_workflow(
    #         "example",
    #         "ETL",
    #         {},
    #         "example",
    #     )
    # )
