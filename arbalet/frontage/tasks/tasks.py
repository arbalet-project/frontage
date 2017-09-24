from __future__ import absolute_import

from .celery import app
from scheduler import Scheduler

@app.task
def start_scheduler():
    scheduler = Scheduler(hardware=False, simulator=False)
    print('---Started')
    scheduler.run()
    print('---Ended')


