import random
import time
from director import task


@task(name="RANDOM")
def generate_random(*args, **kwargs):
    payload = kwargs["payload"]
    for i in range(1):
        time.sleep(5)
        print(f"Task {payload.get('task_id')} - {i}")
    return random.randint(payload.get("start", 0), payload.get("end", 10))


@task(name="ADD")
def add_randoms(*args, **kwargs):
    return sum(args[0])
