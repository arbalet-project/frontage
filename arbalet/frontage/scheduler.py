
import json
import datetime
import time
import sys

from time import sleep
from utils.red import redis, redis_get
from controller import Frontage
from tasks.tasks import start_fap
from tasks.celery import app
from scheduler_state import SchedulerState

from apps.flags import Flags
from apps.random_flashing import RandomFlashing
from apps.sweep_async import SweepAsync
from apps.sweep_rand import SweepRand


def print_flush(s):
    print(s)
    sys.stdout.flush()

TASK_EXPIRATION = 1800


class Scheduler(object):

    def __init__(self, port=33460, hardware=True, simulator=True):
        print_flush('---> Waiting for frontage connection...')
        self.frontage = Frontage(port, hardware)  # Blocking until the hardware client connects
        print_flush('---> Frontage connected')

        redis.set(SchedulerState.KEY_SUNRISE, SchedulerState.DEFAULT_RISE)
        redis.set(SchedulerState.KEY_SUNDOWN, SchedulerState.DEFAULT_DOWN)
        redis.set(SchedulerState.KEY_USERS_Q, '[]')
        redis.set(SchedulerState.KEY_FORCED_APP, False)

        SchedulerState.set_current_app({})

        # Dict { Name: ClassName, Start_at: XXX, End_at: XXX, task_id: XXX}
        self.current_app_state = None
        self.queue = None
        # Struct { ClassName : Instance, ClassName: Instance }
        # app.__class__.__name__
        self.apps = {Flags.__name__: Flags(),
                    SweepAsync.__name__: SweepAsync(),
                    SweepRand.__name__: SweepRand(),
                    RandomFlashing.__name__: RandomFlashing()}

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
    def get_current_user_app(self):
        # Deprecated
        try:
            a = app.control.inspect(['celery@workerqueue']).active()['celery@workerqueue']
            return a
        except Exception, e:
            print_flush(str(e))
            return []

    def keep_alive_waiting_app(self):
        queue = SchedulerState.get_user_app_queue()
        to_remove = []
        i = 0
        for app in queue:
            # Not alive since last check ?
            if time.time() > (app['last_alive'] + SchedulerState.DEFAULT_KEEP_ALIVE_DELAY):
                to_remove.append(i)
            i += 1
        for rm_app in to_remove:
            queue.pop(rm_app)

    def check_scheduler(self):
        if SchedulerState.get_forced_app():
            return

        self.keep_alive_waiting_app()
        queue = SchedulerState.get_user_app_queue()
        c_app = SchedulerState.get_current_app()
        # one task already running
        if c_app:
            # Someone wait for his own task ?
            if len(queue) > 0:
                next_app = queue[0]
                if datetime.datetime.now() > datetime.datetime.strptime(c_app['expire_at'], "%Y-%m-%d %H:%M:%S.%f"):
                    print_flush('===> REVOKING APP, someone else turn')
                    SchedulerState.stop_current_running_app(c_app)
                    # Start app
                    t = start_fap.apply_async(args=[next_app], queue='userapp')
                    # Remove app form waiting Q
                    SchedulerState.pop_user_app_queue(queue)
        else:
            if len(queue) > 0:
                start_fap.apply_async(args=[queue[0]], queue='userapp')
                SchedulerState.pop_user_app_queue(queue)

        # if SchedulerState.get_forced_app():
        #     return
        # if len(self.get_current_user_app()) > 0:
        #     app = SchedulerState.get_current_app()
        #     if datetime.datetime.now() > datetime.datetime.strptime(app['expire_at'], "%Y-%m-%d %H:%M:%S.%f"):
        #         print_flush("-------")
        #         print_flush(self.get_current_user_app()[0])
        #         print_flush("-------")
        #         print_flush('===> REVOKING APP, someone else turn')
        #         revoke(app['task_id'], terminate=True)
        # if len(self.get_current_user_app()) >= 1:
        #     # there is One running task and ONE user waiting to play.
        #     if len(SchedulerState.get_user_app_queue()) >= 1:
        #         pass
        #     else:
        #         pass
        # else:
        #     pass

    def run(self):
        last_state = False
        usable = SchedulerState.usable()
        count = 0
        print_flush('[SCHEDULER] Entering loop')
        # self.running_task = start_fap.apply_async(args=['app1'], queue='userapp')
        self.frontage.start()
        # self.running_task = start_fap.apply_async(args=['Flags', 'user', 'french'], queue='userapp', expires=2)

        while True:
            # Check if usable change
            if (usable != last_state) and last_state is True:
                self.frontage.erase_all()
                self.frontage.update()
                last_state = usable
            # Available, play machine state
            elif SchedulerState.usable():
                self.check_scheduler()

            # Ugly sleep to avoid CPU consuming, not really usefull but I pref use it ATM before advanced tests
            count += 1
            if (count % 500) == 0:
                print_flush('===== Scheduler still running =====')
            sleep(0.5)


def load_day_table(file_name):
    with open(file_name, 'r') as f:
        SUN_TABLE = json.loads(f.read())
        redis.set(SchedulerState.KEY_DAY_TABLE, json.dumps(SUN_TABLE))


if __name__ == '__main__':
    load_day_table(SchedulerState.CITY)
    scheduler = Scheduler(hardware=True)
    scheduler.run()