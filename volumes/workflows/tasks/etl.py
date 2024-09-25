import time
from director import task


@task(name="EXTRACT")
def extract(*args, **kwargs):
    # raise Exception("Error extracting data")
    for i in range(100):
        time.sleep(5)
        print("Elapsed time: {}".format(i*5))
    print("Extracting data")


@task(name="TRANSFORM")
def transform(*args, **kwargs):
    print("Transforming data")


@task(name="LOAD")
def load(*args, **kwargs):
    print("Loading data")
