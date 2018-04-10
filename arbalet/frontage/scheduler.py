
import json
import datetime
import time
import sys

from time import sleep
from utils.red import redis
from frontage import Frontage
from tasks.tasks import start_fap, start_default_fap, clear_all_task
from tasks.celery import app
from scheduler_state import SchedulerState

from apps.fap import Fap
from apps.flags import Flags
from apps.random_flashing import RandomFlashing
from apps.sweep_async import SweepAsync
from apps.sweep_rand import SweepRand
from apps.snap import Snap
from apps.snake import Snake
from apps.tetris import Tetris
from utils.sentry_client import SENTRY

DEBUG = True


def print_flush(s):
    if not DEBUG:
        return
    print(s)
    sys.stdout.flush()


class Scheduler(object):

    def __init__(self, port=33460, hardware=True, simulator=True):
        print_flush('---> Waiting for frontage connection...')
        clear_all_task()
        self.frontage = Frontage(port, hardware)

        redis.set(SchedulerState.KEY_SUNRISE, SchedulerState.DEFAULT_RISE)
        redis.set(SchedulerState.KEY_SUNDOWN, SchedulerState.DEFAULT_DOWN)
        redis.set(SchedulerState.KEY_USERS_Q, '[]')
        redis.set(SchedulerState.KEY_FORCED_APP, False)

        # SchedulerState.set_current_app({})

        # Dict { Name: ClassName, Start_at: XXX, End_at: XXX, task_id: XXX}
        self.current_app_state = None
        self.queue = None
        # Struct { ClassName : Instance, ClassName: Instance }
        # app.__class__.__name__
        self.apps = {Flags.__name__: Flags(),
                     SweepAsync.__name__: SweepAsync(),
                     Snake.__name__: Snake(),
                     SweepRand.__name__: SweepRand(),
                     Snap.__name__: Snap(),
                     Tetris.__name__: Tetris(),
                     RandomFlashing.__name__: RandomFlashing()}

        SchedulerState.set_registered_apps(self.apps)
        # Set schduled time for app, in minutes
        redis.set(SchedulerState.KEY_SCHEDULED_APP_TIME,
                  SchedulerState.DEFAULT_APP_SCHEDULE_TIME)
    # def start_ne

    def get_current_user_app(self):
        # Deprecated
        try:
            a = app.control.inspect(['celery@workerqueue']).active()[
                'celery@workerqueue']
            return a
        except Exception as e:
            print_flush(str(e))
            SENTRY.captureException()
            return []

    def keep_alive_waiting_app(self):
        queue = SchedulerState.get_user_app_queue()
        # i = 0
        for c_app in list(queue):
            # Not alive since last check ?
            if time.time() > (
                    c_app['last_alive'] +
                    SchedulerState.DEFAULT_KEEP_ALIVE_DELAY):
                # to_remove.append(i)
                queue.remove(c_app)
            # i += 1
        # for rm_app in to_remove:
        #     queue.pop(rm_app)

    def check_scheduler(self):
        if SchedulerState.get_forced_app():
            return False

        self.keep_alive_waiting_app()
        queue = SchedulerState.get_user_app_queue()
        c_app = SchedulerState.get_current_app()
        # one task already running
        if c_app:
            # Someone wait for his own task ?
            if len(queue) > 0:
                next_app = queue[0]
                if datetime.datetime.now() > datetime.datetime.strptime(
                        c_app['expire_at'], "%Y-%m-%d %H:%M:%S.%f") or c_app['scheduled_app']:
                    print_flush('===> REVOKING APP, someone else turn')
                    SchedulerState.stop_app(c_app, Fap.CODE_EXPIRE, 'someone else turn')
                    # Start app
                    start_fap.apply_async(args=[next_app], queue='userapp')
                    print_flush("## Starting {} [case A]".format(next_app['name']))
                    # Remove app form waiting Q
                    SchedulerState.pop_user_app_queue(queue)
                    return True
        else:
            # no app runing, app are waiting in queue. We start one
            if len(queue) > 0:
                start_fap.apply_async(args=[queue[0]], queue='userapp')
                print_flush("## Starting {} [case B]".format(queue[0]['name']))
                SchedulerState.pop_user_app_queue(queue)
                return True
            else:
                # No task waiting, start defautl scheduler
                default_scheduled_app = SchedulerState.get_next_default_app()
                # defualt app are schedulled, and stopped auto when expire is outdated.
                # any other app starrted by user has highter
                if default_scheduled_app:
                    next_app = {'name': default_scheduled_app.name,
                                'params': default_scheduled_app.default_params,
                                'username': '>>>default<<<'}
                    # expires => in seconde
                    next_app['expires'] = default_scheduled_app.duration
                    if not next_app['expires'] or next_app['expires'] == 0:
                        next_app['expires'] = (15 * 60)
                    start_default_fap.apply_async(args=[next_app], queue='userapp')
                    SchedulerState.wait_task_to_start()
                    print_flush("## Starting {} [DEFAULT]".format(next_app['name']))
                    return True
        return False

    def run(self):
        last_state = False
        usable = SchedulerState.usable()
        SchedulerState.set_frontage_connected(True)  # TODO ... moved here because it should not prevent the scheduler from starting
        print_flush('[SCHEDULER] Entering loop')
        self.frontage.start()
        count = 0
        while True:
            # Check if usable change
            if (usable != last_state) and last_state is True:
                self.frontage.erase_all()
                last_state = usable
            # Available, play machine state
            elif SchedulerState.usable():
                self.check_scheduler()

            # Update on a regular basis in any case
            sleep(0.1)
            self.frontage.update()
            if count % 50 == 0:
                print_flush("-------- Current App")
                print_flush(SchedulerState.get_current_app())
                print_flush("---------- Waiting Queue")
                print_flush(SchedulerState.get_user_app_queue())
                print_flush(" ========== Scheduling ==========")
            count += 1

        print_flush('===== Scheduler End =====')


def load_day_table(file_name):
    with open(file_name, 'r') as f:
        SUN_TABLE = json.loads(f.read())
        redis.set(SchedulerState.KEY_DAY_TABLE, json.dumps(SUN_TABLE))


if __name__ == '__main__':
    try:
        load_day_table(SchedulerState.CITY)
        scheduler = Scheduler(hardware=True)
        scheduler.run()
        print_flush('=== Scheduler Stop ===')
    except Exception as e:
        print_flush('=== Scheduler Exception ===')
        print_flush(e)
        print_flush('===========================')
        SENTRY.captureException()
