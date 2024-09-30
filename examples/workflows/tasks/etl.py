import time
from director import task


@task(name="EXTRACT")
def extract(*args, **kwargs):
    extract.logger.info("Extracting data")
    
    # raise Exception("Error extracting data")
    for i in range(10):
        time.sleep(1)
        extract.logger.info("Elapsed time: {}".format(i*1))
    extract.logger.info("Extracting data")


@task(name="TRANSFORM")
def transform(*args, **kwargs):
    transform.logger.info("Transforming data")
    


@task(name="LOAD")
def load(*args, **kwargs):
    load.logger.info("Loading data")
    for i in range(10):
        time.sleep(1)
        load.logger.info("Elapsed time: {}".format(i*5))

