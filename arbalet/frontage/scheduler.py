import json
import datetime
import sys

from time import sleep
from utils.red import redis, redis_get
from controller import Frontage
from apps.flags import Flags
from tasks.tasks import start_fap
from tasks.celery import app
from scheduler_state import SchedulerState

def print_flush(s):
    print(s)
    sys.stdout.flush()

TASK_EXPIRATION=1800

class Scheduler(object):

    def __init__(self, port=33460, hardware=True, simulator=True):
        print_flush('---> Waiting for frontage connection...')
        self.frontage = Frontage(port, hardware)  # Blocking until the hardware client connects
        print_flush('---> Frontage connected')

        redis.set(SchedulerState.KEY_SUNRISE, SchedulerState.DEFAULT_RISE)
        redis.set(SchedulerState.KEY_SUNDOWN, SchedulerState.DEFAULT_DOWN)
        SchedulerState.set_current_app('{}')

        # Dict { Name: ClassName, Start_at: XXX, End_at: XXX, task_id: XXX}
        self.current_app_state = None
        self.queue = None
        # Struct { ClassName : Instance, ClassName: Instance }
        # app.__class__.__name__
        self.apps = {Flags.__name__: Flags(self.frontage)}
        SchedulerState.set_registered_apps(self.apps)
        # Set schduled time for app, in minutes
        redis.set(SchedulerState.KEY_SCHEDULED_APP_TIME, SchedulerState.DEFAULT_APP_SCHEDULE_TIME)


    # def start_next_app(self):
    #     app = {}
    #     app['name'] = redis.lindex(SchedulerState.KEY_SCHEDULED_APP, 0)
    #     app['end_at'] = datetime.datetime.now() + datetime.timedelta(minutes=SchedulerState.DEFAULT_APP_SCHEDULE_TIME)
    #     app['user'] = ""

    #     self.current_app_state = app
    #     app_rdis = app.copy()
    #     app_rdis['end_at'] = app['end_at'].strftime('%Y-%m-%d %H:%M:%S.%f')
    #     redis.hmset(KEY_CURRENT_RUNNING_APP, app_rdis)

    # def play_current_app(self):
    #     if self.current_app_state:
    #         # Shgoudl the app stop and let the other one play ?
    #         if self.current_app_state.end_at < datetime.datetime.now():
    #             print(' App end, go to next')
    #             # Remove 1st item, and put it in the end (circular fifo)
    #             old_current = redis.lpop(SchedulerState.KEY_SCHEDULED_APP)
    #             redis.rpush(SchedulerState.KEY_SCHEDULED_APP, old_current)
    #             self.start_next_app()
    #         print(' BlaBLa Im running Bru` ')

    def start_queued_app(self):
        pass

    def start_scheduled_app(self):
        pass

    def get_user_app_queue(self):
        return app.control.inspect(['celery@workerqueue']).reserved()['celery@workerqueue']

    def get_current_user_app(self):
        try:
            a = app.control.inspect(['celery@workerqueue']).active()['celery@workerqueue']
            return a
        except Exception, e:
            print_flush(str(e))
            return []

    def check_scheduler(self):
        if SchedulerState.get_forced_app():
            return
        if len(self.get_current_user_app()) >= 1:
            # there is One running task and ONE user waiting to play.
            if len(self.get_user_app_queue()) >= 1:
                pass
            else:
                pass
        else:
            pass

    def run(self):
        last_state = False
        usable = SchedulerState.usable()
        count = 0
        print('[SCHEDULER] Entering loop')
        # self.running_task = start_fap.apply_async(args=['app1'], queue='userapp')
        self.frontage.start()

        while True:
            # Check if usable change
            if (usable != last_state) and last_state == True:
                self.frontage.erase_all()
                self.frontage.update()
                last_state = usable
            # Available, play machine state
            elif SchedulerState.usable():
                self.check_scheduler()
            ## self.running_task = start_fap.apply_async(args=['Flags'], queue='userapp', expires=TASK_EXPIRATION)

            # Ugly sleep to avoid CPU consuming, not really usefull but I pref use it ATM before advanced tests
            count += 1
            if (count % 500) == 0:
                # self.running_task = start_fap.apply_async(args=['TestApp'], queue='userapp', expires=TASK_EXPIRATION)
                print_flush('=============> Scheduler is stil running around...')
            sleep(0.02)


if __name__ == '__main__':
    scheduler = Scheduler(hardware=False)
    scheduler.run()