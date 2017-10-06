from __future__ import absolute_import

import datetime

from .celery import app
from scheduler_state import SchedulerState
from apps.flags import Flags

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
            fap.run()
        except Exception, e:
            print(str(e))




