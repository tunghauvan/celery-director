import os
import sys
from director import task

def update_change_request(*args, **kwargs):
    print("Updating change request")
    return "Change request updated"

@task(name="update_change_request")
def update_change_request_task(*args, **kwargs):
    return update_change_request(*args, **kwargs)