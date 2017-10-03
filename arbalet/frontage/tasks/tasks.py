from __future__ import absolute_import

from .celery import app
from scheduler_state import SchedulerState
from apps.flags import Flags

def TestApp():
    print('[TASK] Running a test app. Im doing nothing at all')

@app.task
def start_fap(fap_name=None, user_name='Anonymous'):
    SchedulerState.set_app_started_at()
    if fap_name:
    	try:
        	globals()[fap_name]()
        except Exception, e:
        	print(str(e))




