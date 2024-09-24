# sdk/workflow.py

from director import create_app
from director.models.workflows import Workflow
from director.extensions import cel_workflows
from director.api import validate
from director.builder import WorkflowBuilder
from director.exceptions import WorkflowNotFound
from flask import abort, current_app as app

class WorkflowSDK:
    def __init__(self):
        self.app = create_app()
        self.cel_workflows = cel_workflows

    def create_workflow(self, project, name, payload, comment=None):
        """
        Create a new workflow in the database.
        
        :param project: The project name.
        :param name: The workflow name.
        :param payload: The workflow payload.
        :param comment: Optional comment for the workflow.
        :return: Dictionary representation of the created workflow.
        """
        fullname = f"{project}.{name}"

        # Check if the workflow exists
        try:
            wf = self.cel_workflows.get_by_name(fullname)
            if "schema" in wf:
                validate(payload, wf["schema"])
        except WorkflowNotFound:
            print(f"Workflow {fullname} not found")
        
        self.cel_workflows.add_workflow(fullname, payload)

        # Create the workflow in DB
        obj = Workflow(project=project, name=name, payload=payload, comment=comment)
        obj.save()

        return obj.to_dict()

    def list_workflows(self):
        """
        List all workflows in the database.
        
        :return: List of dictionaries representing workflows.
        """
        workflows = []
        for fullname, definition in sorted(self.cel_workflows.workflows.items()):
            workflows.append({fullname: definition})
        return workflows

    def update_workflow(self, project, name, payload, comment=None):
        """
        Update an existing workflow in the database.
        
        :param project: The project name.
        :param name: The workflow name.
        :param payload: The updated workflow payload.
        :param comment: Optional comment for the workflow.
        :return: Dictionary representation of the updated workflow.
        """
        fullname = f"{project}.{name}"

        # Check if the workflow exists
        try:
            wf = self.cel_workflows.get_by_name(fullname)
            if "schema" in wf:
                validate(payload, wf["schema"])
        except WorkflowNotFound:
            print(f"Workflow {fullname} not found")
        
        self.cel_workflows.update_workflow(fullname, payload)

        # Create the workflow in DB
        obj = Workflow(project=project, name=name, payload=payload, comment=comment)
        obj.save()

        return obj.to_dict()

    def execute_workflow(self, project, name, payload={}, comment=None):
        """
        Execute a workflow.
        
        :param project: The project name.
        :param name: The workflow name.
        :param payload: Parameters for the workflow execution.
        :param comment: Optional comment for the workflow.
        :return: Result of the workflow execution.
        """

        fullname = f"{project}.{name}"
        
        # app = create_app()
        
        # # Check if the workflow exists
        # try:
        #     wf = self.cel_workflows.get_by_name(fullname)
        #     if "schema" in wf:
        #         validate(payload, wf["schema"])
        # except WorkflowNotFound:
        #     abort(404, f"Workflow {fullname} not found")

        # Create the workflow in DB
        obj = Workflow(project=project, name=name, payload=payload, comment=comment)
        obj.save()

        # Build the workflow and execute it
        data = obj.to_dict()
        workflow = WorkflowBuilder(obj.id)
        workflow.run()

        app.logger.info(f"Workflow sent : {workflow.canvas}")

        return obj.to_dict(), workflow

# Example usage
if __name__ == '__main__':
    app = create_app()
    sdk = WorkflowSDK()
    sdk.create_workflow('example', 'RANDOMS_V2', {'tasks': ['RANDOM']})
    print('-'*80)
    for wf in sdk.list_workflows():
        print("Workflow: name={}, payload={}".format(list(wf.keys())[0], list(wf.values())[0]))
    # sdk.update_workflow('example', 'RANDOMS_V2', {'tasks': ['EXTRACT', 'TRANSFORM', 'LOAD', 'TEST']})
    # print('-'*80)
    # for wf in sdk.list_workflows():
    #     print("Workflow: name={}, payload={}".format(list(wf.keys())[0], list(wf.values())[0]))
    
    # run workflow
    print(sdk.execute_workflow(
        'example',
        'RANDOMS_V2',
        {}
    ))