
import json
import datetime
import time
import logging

from time import sleep
from utils.red import redis
from frontage import Frontage
from tasks.tasks import start_fap, start_default_fap, start_forced_fap, clear_all_task
from collections import OrderedDict
from scheduler_state import SchedulerState

from apps.fap import Fap
from db.base import Base
from utils.sentry_client import SENTRY
from utils.websock import Websock
from apps import *


EXPIRE_SOON_DELAY = 30
logging.basicConfig(level=logging.INFO)

class Scheduler(object):
    def __init__(self):
        clear_all_task()

        redis.set(SchedulerState.KEY_USERS_Q, '[]')
        redis.set(SchedulerState.KEY_FORCED_APP, 'False')
        Websock.set_grantUser({'id': "turnoff", 'username':"turnoff"})

        self.frontage = Frontage()
        self.current_app_state = None
        self.queue = None
        self.count = 0
        self.apps = OrderedDict([(app, globals()[app]('', '')) for app in get_app_names()])
        SchedulerState.set_registered_apps(self.apps)


    def keep_alive_waiting_app(self):
        queue = SchedulerState.get_user_app_queue()
        for c_app in list(queue):
            # Not alive since last check ?
            if time.time() > (
                    c_app['last_alive'] +
                    SchedulerState.DEFAULT_KEEP_ALIVE_DELAY):
                # to_remove.append(i)
                queue.remove(c_app)

    def keep_alive_current_app(self, current_app):
        if not current_app.get('is_default', False) and not current_app.get('is_forced', False) and \
                        time.time() > (current_app['last_alive'] + SchedulerState.DEFAULT_CURRENT_APP_KEEP_ALIVE_DELAY):
            self.stop_app(current_app, None, 'User has disappeared')
            return True
        return False

    def check_on_off_table(self):
        now = datetime.datetime.now()
        sunrise = SchedulerState.get_scheduled_off_time()
        sunset = SchedulerState.get_scheduled_on_time()

        if sunset < now and now < sunrise:
            SchedulerState.set_frontage_on(True)
        else:
            SchedulerState.set_frontage_on(False)

    def disable_frontage(self):
        SchedulerState.clear_user_app_queue()
        c_app = SchedulerState.get_current_app()
        if c_app:
            self.stop_app(c_app,
                        Fap.CODE_CLOSE_APP,
                        'The admin disabled Arbalet Frontage')

    def stop_app(self, c_app, stop_code=None, stop_message=None):
        # flask_log(" ========= STOP_APP ====================")
        if not c_app or 'task_id' not in c_app:
            logging.error('Cannot stop invalid app')
            return

        from tasks.celery import app
        if not c_app.get('is_default', False) and not c_app.get('is_forced', False):
            if stop_code and stop_message and 'userid' in c_app:
                Websock.send_data(stop_code, stop_message, c_app['username'], c_app['userid'])

        app.control.revoke(c_app['task_id'], terminate=True)
        self.frontage.fade_out()
        SchedulerState.set_current_app({})


    def run_scheduler(self):
        # check usable value, based on ON/OFF AND if a forced app is running
        SchedulerState.set_usable((not SchedulerState.get_forced_app()) and SchedulerState.is_frontage_on())
        enable_state = SchedulerState.get_enable_state()
        if enable_state == 'scheduled':
            self.check_on_off_table()
        elif enable_state == 'on':
            SchedulerState.set_frontage_on(True)
        elif enable_state == 'off':
            SchedulerState.set_frontage_on(False)

        if SchedulerState.is_frontage_on():
            self.check_app_scheduler()
        else:
            # improvement : add check to avoid erase in each loop
            self.disable_frontage()
            self.frontage.erase_all()

    def stop_current_app_start_next(self, queue, c_app, next_app):
        SchedulerState.set_event_lock(True)
        logging.info('## Revoking app [stop_current_app_start_next]')
        self.stop_app(c_app, Fap.CODE_EXPIRE, 'Someone else turn')
        # Start app
        logging.info("## Starting {} [stop_current_app_start_next]".format(next_app['name']))
        start_fap.apply_async(args=[next_app], queue='userapp')
        SchedulerState.wait_task_to_start()

    def app_is_expired(self, c_app):
        now = datetime.datetime.now()
        return now > datetime.datetime.strptime(c_app['expire_at'], "%Y-%m-%d %H:%M:%S.%f")

    def start_default_app(self):
        default_scheduled_app = SchedulerState.get_next_default_app()
        if default_scheduled_app:
            # if not default_scheduled_app['expires'] or default_scheduled_app['expires'] == 0: # TODO restore when each default app has a duration
            #    default_scheduled_app['expires'] = SchedulerState.get_default_fap_lifetime()
            default_scheduled_app['expires'] = SchedulerState.get_default_fap_lifetime()
            default_scheduled_app['default_params']['name'] = default_scheduled_app['name']  # Fix for Colors (see TODO refactor in colors.py)
            SchedulerState.set_event_lock(True)

            logging.info("## Starting {} [DEFAULT]".format(default_scheduled_app['name']))
            start_default_fap.apply_async(args=[default_scheduled_app], queue='userapp')
            SchedulerState.wait_task_to_start()

    def check_app_scheduler(self):
        # check keep alive app (in user waiting app Q)
        self.keep_alive_waiting_app()

        # collect usefull struct & data
        queue = SchedulerState.get_user_app_queue()  # User waiting app
        c_app = SchedulerState.get_current_app()  # Current running app
        now = datetime.datetime.now()

        forced_app = SchedulerState.get_forced_app_request()

        # Is a app running ?
        if c_app:
            close_request, close_userid = SchedulerState.get_close_app_request()
            if close_request:
                message = Fap.CODE_CLOSE_APP if close_userid != c_app['userid'] else None
                logging.info('## Stopping app upon user reques [check_app_scheduler]')
                self.stop_app(c_app, message, 'Executing requested app closure')
                redis.set(SchedulerState.KEY_STOP_APP_REQUEST, '{}')
                return
            if len(forced_app) > 0 and not SchedulerState.get_forced_app():
                logging.info('## Closing previous app for forced one [check_app_scheduler]')
                SchedulerState.clear_user_app_queue()
                self.stop_app(c_app, Fap.CODE_CLOSE_APP, 'The admin started a forced app')
                return
            # do we kill an old app no used ? ?
            if self.keep_alive_current_app(c_app):
                return
            # is expire soon ?
            if not c_app.get('is_default', False) and now > (datetime.datetime.strptime(c_app['expire_at'], "%Y-%m-%d %H:%M:%S.%f") - datetime.timedelta(seconds=EXPIRE_SOON_DELAY)):
                if not SchedulerState.get_expire_soon():
                    Fap.send_expires_soon(EXPIRE_SOON_DELAY, c_app['username'], c_app['userid'])
            # is the current_app expired ?
            if self.app_is_expired(c_app) or c_app.get('is_default', False):
                # is the current_app a FORCED_APP ?
                if SchedulerState.get_forced_app():
                    logging.info('## Stopping expired forced app [check_app_scheduler]')
                    self.stop_app(c_app)
                    return
                # is some user-app are waiting in queue ?
                if len(queue) > 0:
                    next_app = queue[0]
                    self.stop_current_app_start_next(queue, c_app, next_app)
                    return
                else:
                    # is a defautl scheduled app ?
                    if c_app.get('is_default', False) and self.app_is_expired(c_app):
                        logging.info('## Stopping expired default scheduled app [check_app_scheduler]')
                        self.stop_app(c_app)
                        return
                    # it's a USER_APP, we let it running, do nothing
                    else:
                        pass
        else:
            if len(forced_app) > 0 and not SchedulerState.get_forced_app():
                logging.info("## Starting {} [FORCED]".format(forced_app['name']))
                SchedulerState.set_event_lock(True)
                SchedulerState.clear_forced_app_request()
                start_forced_fap.apply_async(args=[forced_app], queue='userapp')
                redis.set(SchedulerState.KEY_FORCED_APP, 'True')
                return
            # is an user-app waiting in queue to be started ?
            elif len(queue) > 0:
                SchedulerState.set_event_lock(True)
                start_fap.apply_async(args=[queue[0]], queue='userapp')
                logging.info(" Starting {} [QUEUE]".format(queue[0]['name']))
                return
            else:
                return self.start_default_app()

    def print_scheduler_info(self):
        if self.count % 100 == 0:
            self.count = 0
            logging.info(" ========== Scheduling ==========")
            logging.info("-------- Geometry")
            logging.info("\t\t {} rows * {} cols".format(SchedulerState.get_rows(), SchedulerState.get_cols()))
            logging.info("-------- Disabled")
            logging.info("\t\t {}".format(SchedulerState.get_disabled()))
            logging.info("-------- Enable State")
            logging.info(SchedulerState.get_enable_state())
            logging.info("-------- Is Frontage Up?")
            logging.info(SchedulerState.is_frontage_on())
            logging.info("-------- Usable?")
            logging.info(SchedulerState.usable())
            logging.info("-------- Current App")
            logging.info(SchedulerState.get_current_app())
            logging.info('Forced App ? {}'.format(SchedulerState.get_forced_app()))
            logging.info("---------- Waiting Queue")
            logging.info(SchedulerState.get_user_app_queue())
            if SchedulerState.get_enable_state() == 'scheduled':
                logging.info("---------- Scheduled ON")
                logging.info(SchedulerState.get_scheduled_on_time())
                logging.info("---------- Scheduled OFF")
                logging.info(SchedulerState.get_scheduled_off_time())
        self.count += 1

    def update_geometry(self):
        SchedulerState.update_geometry(SchedulerState.get_rows(), SchedulerState.get_cols(), SchedulerState.get_disabled())

    def run(self):
        # last_state = False
        # we reset the value
        SchedulerState.set_frontage_on(True)
        SchedulerState.set_enable_state(SchedulerState.get_enable_state())
        # usable = SchedulerState.usable()
        logging.info('[SCHEDULER] Entering loop')
        self.frontage.start()
        try:
            while True:
                if SchedulerState.is_event_lock():
                    logging.info('Locked')
                else:
                    self.run_scheduler()
                    self.update_geometry()
                    self.print_scheduler_info()
                sleep(0.1)
        except:
            raise
        finally:
            pass
            self.frontage.close()


def load_day_table(file_name):
    with open(file_name, 'r') as f:
        SUN_TABLE = json.loads(f.read())
        redis.set(SchedulerState.KEY_DAY_TABLE, json.dumps(SUN_TABLE))

if __name__ == '__main__':
    try:
        load_day_table(SchedulerState.CITY)
        SchedulerState.check_db()
        scheduler = Scheduler()
        scheduler.run()
    except:
        SENTRY.captureException()
        raise   # Re-raise since Docker will restart the scheduler
