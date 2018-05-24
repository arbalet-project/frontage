from __future__ import absolute_import
from __future__ import print_function

import datetime
import time

from logging import INFO

from server.extensions import celery
from celery.utils.log import get_task_logger
from server.flaskutils import print_flush

from scheduler_state import SchedulerState
from utils.red import redis, redis_get
from apps.flags import Flags
from apps.random_flashing import RandomFlashing
from apps.sweep_async import SweepAsync
from apps.sweep_rand import SweepRand
from apps.snake import Snake
from apps.tetris import Tetris
from apps.snap import Snap

class TestApp():
    def run(self, params):
        print('[TASK] Running a test app. Im doing nothing at all')
        while True:
            pass

def clear_all_task():
    celery.control.purge()
    SchedulerState.set_current_app({})
    SchedulerState.set_event_lock(False)

@celery.task
def start_default_fap(app):
    SchedulerState.set_app_started_at()
    # app['expire_at'] = str(
    #     datetime.datetime.now())
    if 'params' not in app:
        app['params'] = {}
    app['expire_at'] = str(
        datetime.datetime.now() +
        datetime.timedelta(
            seconds=app['expires']))

    params = app['default_params'].copy()
    params.update(app['params'])

    app['task_id'] = start_default_fap.request.id
    app['is_default'] = True
    app['is_forced'] = False
    app['last_alive'] = time.time()
    app['username'] = '>>>default<<<'
    app['userid'] = '>>>default<<<'
    app['started_at'] = datetime.datetime.now().isoformat()

    SchedulerState.set_current_app(app)
    SchedulerState.set_event_lock(False)
    fap = globals()[app['name']](app['username'], app['userid'])
    try:
        fap.run(params=params)
    finally:
        fap.close()
        SchedulerState.set_current_app({})


@celery.task
def start_fap(app):
    SchedulerState.set_app_started_at()
    app['expire_at'] = str(
        datetime.datetime.now() +
        datetime.timedelta(
            seconds=app['expires']))
    app['is_default'] = False
    app['is_forced'] = False
    app['task_id'] = start_fap.request.id
    app['started_at'] = datetime.datetime.now().isoformat()
    SchedulerState.pop_user_app_queue()
    SchedulerState.set_current_app(app)
    SchedulerState.set_event_lock(False)
    fap = globals()[app['name']](app['username'], app['userid'])

    try:
        fap.run(params=app['params'], expires_at=app['expire_at'])
    finally:
        fap.close()
        SchedulerState.set_current_app({})


@celery.task
def start_forced_fap(fap):
    SchedulerState.clear_user_app_queue()
    SchedulerState.set_app_started_at()
    name = fap['name']
    params = fap['params']

    app = {
        'name': name,
        'username': '>>>>FORCED<<<<',
        'userid': '>>>>FORCED<<<<',
        'params': fap['params'],
        'task_id': start_forced_fap.request.id,
        'last_alive': time.time(),
        'started_at': datetime.datetime.now().isoformat(),
        'is_default': False,
        'is_forced': True,
        'expire_at': str(datetime.datetime.now() + datetime.timedelta(weeks=52))}
    SchedulerState.set_current_app(app)
    SchedulerState.set_event_lock(False)
    fap = globals()[name](app['username'], app['userid'])
    try:
        fap.run(params=params)
        return True
    finally:
        fap.close()
        redis.set(SchedulerState.KEY_FORCED_APP, 'False')
        SchedulerState.set_current_app({})
