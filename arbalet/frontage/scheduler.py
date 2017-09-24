import json
import datetime

from time import sleep
from utils.red import redis, redis_get
from controller import Frontage

DEFAULT_RISE = '2017-07-07 01:00:00.000000'
DEFAULT_DOWN = '2017-07-07 22:00:00.000000'

class Scheduler(object):

    KEY_USABLE = 'frontage_usable'
    KEY_MODEL = 'frontage_model'
    KEY_SUNDOWN = 'frontage_sundown'
    KEY_SUNRISE = 'frontage_sunrise'
    KEY_SUN_STATE = 'frontage_sunstate'
    KEY_REGISTERED_APP = 'frontage_registered_app'
    KEY_SCHEDULED_APP = 'frontage_scheduler_app'
    KEY_SCHEDULED_APP_TIME = 'frontage_scheduler_app_time'

    def __init__(self, port=33460, hardware=True, simulator=True):

        redis.set(Scheduler.KEY_SUNRISE, DEFAULT_RISE)
        redis.set(Scheduler.KEY_SUNDOWN, DEFAULT_DOWN)

        # Dict { Name: ClassName, Start_at: XXX, End_at: XXX}
        self.current_app_state = None
        # Struct { ClassName : Instance, ClassName: Instance }
        # app.__class__.__name__
        self.apps = {}
        # Set schduled tiem for app, in minutes
        redis.set(Scheduler.KEY_SCHEDULED_APP_TIME, 15)
        self.frontage = Frontage(port, hardware, simulator)  # Blocking until the hardware client connects
        pass
    """ Is scheduller on or off ATM ?"""
    @staticmethod
    def usable():
        val = redis_get(Scheduler.KEY_USABLE)
        return val == "True"

    @staticmethod
    def set_usable(value):
        redis.set(Scheduler.KEY_USABLE, str(value))

    @staticmethod
    def default_scheduled_time():
        return redis_get(Scheduler.KEY_SCHEDULED_APP_TIME)

    @staticmethod
    def get_sunrise():
        v = redis_get(Scheduler.KEY_SUNRISE, DEFAULT_RISE)
        return datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def get_sundown():
        v = redis_get(Scheduler.KEY_SUNDOWN, DEFAULT_DOWN)
        return datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def get_scheduled_apps():
        try:
            apps = redis.lrange(Scheduler.KEY_SCHEDULED_APP, 0, -1)
        except Exception, e:
            print('Error, empty list')
        if apps:
            return apps
        return []

    @staticmethod
    def get_available_apps():
        return redis.hgetall(Scheduler.KEY_REGISTERED_APP)

    @staticmethod
    def add_schedule_app(app_name):
        apps = Scheduler.get_scheduled_apps()
        if app_name in apps:
            return
        redis.rpush(Scheduler.KEY_SCHEDULED_APP, app_name)

    def play_current_app(self):
        if self.current_app_state:
            # Shgoudl the app stop and let the other one play ?
            if self.current_app_state.end_at < datetime.datetime.now():
                print(' App end, go to next')
                # Remove 1st item, and put it in the end (circular fifo)
                old_current = redis.lpop(Scheduler.KEY_SCHEDULED_APP)
                redis.rpush(Scheduler.KEY_SCHEDULED_APP, old_current)
                self.current_app_state = redis.lindex(Scheduler.KEY_SCHEDULED_APP, 0)
            print(' BlaBLa Im running Bru` ')

    def run(self):
        last_state = False
        usable = Scheduler.usable()
        count = 0
        while True:
            # Check if usable change
            if (usable != last_state) and last_state == True:
                self.frontage.erase_all()
            # Available, play machien state
            if Scheduler.usable():
                self.play_current_app()

            # Ugly sleep to avoid CPU consuming, not really usefull but I pref use it ATM before advanced tests
            count += 1
            print('')
            if (count % 1000) == 0:
                print('=============> Scheduler is stil running around...')
            sleep(0.005)
