from __future__ import absolute_import

import json
import datetime


from celery import Celery
from scheduler import Scheduler
from utils.red import redis, redis_get

app = Celery('tasks', backend='redis://redis', broker='redis://redis', include=['tasks.tasks', 'tasks'])

SUNRISE = ''

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        10.0,
        check_sunrise_sunset.s()
    )

@app.task
def check_sunrise_sunset():
    print('[CELERY] {PERIODIC} Check Sunrise & Sunset}')

    state = redis_get(Scheduler.KEY_SUN_STATE)
    now = datetime.datetime.now()

    if state == Scheduler.KEY_SUNRISE:
        if now.time() > Scheduler.get_sundown().time():
            state = redis.set(Scheduler.KEY_SUN_STATE, Scheduler.KEY_SUNDOWN)
            Scheduler.set_usable(True)
    else:
        if now.time() > Scheduler.get_sunrise().time():
            state = redis.set(Scheduler.KEY_SUN_STATE, Scheduler.KEY_SUNRISE)
            Scheduler.set_usable(False)
    return True


def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the backend server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d

if __name__ == '__main__':
    print('=========== STARTED CELERY IN MAIN MODE ===========')
    app.start()