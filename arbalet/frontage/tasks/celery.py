from __future__ import absolute_import

import datetime

from server.extensions import celery
from server.app import create_app
from scheduler_state import SchedulerState
from utils.red import redis, redis_get

app = celery
app.init_app(create_app())

SUNRISE = ''


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        60.0,
        check_sunrise_sunset.s()
    )


@app.task
def check_sunrise_sunset():
    # print('[CELERY] {PERIODIC} Check Sunrise & Sunset}')

    # state = redis_get(SchedulerState.KEY_SUN_STATE)
    now = datetime.datetime.now().time()

    on_at = SchedulerState.get_sundown().time()
    off_at = SchedulerState.get_sunrise().time()

    if not SchedulerState.get_enable_state() == 'scheduled':
        return True
    if now < off_at:
        redis.set(SchedulerState.KEY_SUN_STATE, SchedulerState.KEY_SUNDOWN)
        SchedulerState.set_usable(True)
    elif now > off_at and now < on_at:
        redis.set(SchedulerState.KEY_SUN_STATE, SchedulerState.KEY_SUNRISE)
        SchedulerState.set_usable(False)
    elif now > off_at and now > on_at:
        redis.set(SchedulerState.KEY_SUN_STATE, SchedulerState.KEY_SUNDOWN)
        SchedulerState.set_usable(True)

    # if state == SchedulerState.KEY_SUNRISE:
    #     if now.time() > SchedulerState.get_sundown().time():
    #         state = redis.set(SchedulerState.KEY_SUN_STATE, SchedulerState.KEY_SUNDOWN)
    #         SchedulerState.set_usable(True)
    # else:
    #     if now.time() > SchedulerState.get_sunrise().time():
    #         state = redis.set(SchedulerState.KEY_SUN_STATE, SchedulerState.KEY_SUNRISE)
    #         SchedulerState.set_usable(False)
    return True


def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = {ERROR_KEY: 'No running Celery workers were found.'}
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the backend server is running.'
        d = {ERROR_KEY: msg}
    except ImportError as e:
        d = {ERROR_KEY: str(e)}
    return d


if __name__ == '__main__':
    print('=========== STARTED CELERY IN MAIN MODE ===========')
    app.start()
