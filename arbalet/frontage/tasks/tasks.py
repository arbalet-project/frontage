from __future__ import absolute_import
from __future__ import print_function

import datetime
import sys

from time import sleep

from server.extensions import celery
from celery.task.control import revoke
from celery import current_task

from scheduler_state import SchedulerState
from utils.red import redis, redis_get
from apps.flags import Flags
from apps.random_flashing import RandomFlashing
from apps.sweep_async import SweepAsync
from apps.sweep_rand import SweepRand
from apps.snake import Snake
from apps.tetris import Tetris


class TestApp():
    def run(self, params):
        print('[TASK] Running a test app. Im doing nothing at all')
        while True:
            pass


def flask_log(msg):
    print(msg, file=sys.stderr)


def clear_all_task():
    celery.control.purge()
    if current_task:
        revoke(current_task.request.id, terminate=True)
    sleep(0.5)
    SchedulerState.set_current_app({})


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
    app['task_id'] = start_default_fap.request.id
    app['scheduled_app'] = True
    app['started_at'] = datetime.datetime.now().isoformat()

    SchedulerState.set_current_app(app)
    try:
        fap = globals()[app['name']]()
        fap.run(params=app['params'])
    except Exception as e:
        print('--->APP>>')
        del fap
        print('Error when starting task ' + str(e))
        # raise e
    finally:
        SchedulerState.set_current_app({})


@celery.task
def start_fap(app):
    SchedulerState.set_app_started_at()
    app['expire_at'] = str(
        datetime.datetime.now() +
        datetime.timedelta(
            seconds=app['expires']))
    app['scheduled_app'] = False
    app['task_id'] = start_fap.request.id
    app['started_at'] = datetime.datetime.now().isoformat()

    SchedulerState.set_current_app(app)
    try:
        fap = globals()[app['name']]()
        fap.run(params=app['params'], expires_at=app['expire_at'])
    except Exception as e:
        print('--->APP>>')
        print('Error when starting task ' + str(e))
        raise e
        return 'Error when starting task ' + str(e)
    finally:
        flask_log('--======================== ENDED START_APP')
        SchedulerState.set_current_app({})


@celery.task
def start_forced_fap(fap_name=None, user_name='Anonymous', params=None):
    if redis_get(SchedulerState.KEY_FORCED_APP, False) == 'True':
        print('-----------------------')
        print(SchedulerState.get_current_app())
        print('-----------------------')
        print('A forced App is already running')
        print('-----------------------')
        return

    SchedulerState.set_app_started_at()
    app_struct = {
        'name': fap_name,
        'username': user_name,
        'params': params,
        'task_id': start_forced_fap.request.id,
        'started_at': datetime.datetime.now().isoformat()}
    SchedulerState.set_current_app(app_struct)
    if fap_name:
        try:
            fap = globals()[fap_name]()
            redis.set(SchedulerState.KEY_FORCED_APP, True)
            fap.run(params=params)
            return True
        except Exception as e:
            print('Error when starting task ' + str(e))
            raise
        finally:
            redis.set(SchedulerState.KEY_FORCED_APP, False)
            SchedulerState.set_current_app({})
    return True
