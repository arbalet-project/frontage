from __future__ import absolute_import

import datetime

from .celery import app
from scheduler_state import SchedulerState
from utils.red import redis
from apps.flags import Flags
from apps.colors import Colors

class TestApp():
    def run(self, params):
        print('[TASK] Running a test app. Im doing nothing at all')
        while True:
            pass

@app.task
def start_fap(fap_name=None, user_name='Anonymous', params=None):
    SchedulerState.set_app_started_at()
    app_struct = {'name': fap_name, 'username': user_name, 'params': params, 'started_at': datetime.datetime.now().isoformat() }
    SchedulerState.set_current_app(app_struct)
    if fap_name:
        try:
            fap = globals()[fap_name]()
            fap.run(params=params)
        except Exception, e:
            print('Error when starting task'+str(e))
            return 'Error when starting task'+str(e)


@app.task
def start_forced_fap(fap_name=None, user_name='Anonymous', params=None):
    SchedulerState.set_app_started_at()
    app_struct = {'name': fap_name, 'username': user_name, 'params': params, 'started_at': datetime.datetime.now().isoformat() }
    SchedulerState.set_current_app(app_struct)
    if fap_name:
        try:
            fap = globals()[fap_name]()
            redis.set(SchedulerState.KEY_FORCED_APP, True)
            fap.run(params=params)
            return True
        except Exception, e:
            print('Error when starting task '+str(e))
            raise
        finally:
            redis.set(SchedulerState.KEY_FORCED_APP, False)
    return True



