import json
import datetime
import sys

from time import sleep
from utils.red import redis, redis_get




class SchedulerState(object):

    DEFAULT_RISE = '2017-07-07 01:00:00.000000'
    DEFAULT_DOWN = '2017-07-07 22:00:00.000000'
    DEFAULT_USER_OCCUPATION = 120 # in seconde
    DEFAULT_APP_SCHEDULE_TIME = 15 # in minutes

    KEY_USABLE = 'frontage_usable'
    KEY_MODEL = 'frontage_model'
    KEY_SUNDOWN = 'frontage_sundown'
    KEY_SUNRISE = 'frontage_sunrise'
    KEY_SUN_STATE = 'frontage_sunstate'
    KEY_REGISTERED_APP = 'frontage_registered_app'
    KEY_APP_STARTED_AT = 'frontage_app_started_at'

    KEY_SCHEDULED_APP_TIME = 'frontage_scheduler_app_time'

    # Default planned apps
    KEY_SCHEDULED_APP = 'frontage_scheduler_app'
    # admin override app
    KEY_FORCED_APP = 'frontage_forced_app'
    # App started by user, (queued)
    KEY_USERS_Q = 'frontage_users_q'

    KEY_CURRENT_RUNNING_APP = 'frontage_current_running_app'
    """KEY_CURRENT_USER = 'frontage_current_user'"""

    @staticmethod
    def get_forced_app():
        # add callback on frocer_app_task_launcher to set variable to false when done
        return redis_get(SchedulerState.KEY_FORCED_APP, False)

    @staticmethod
    def set_registered_apps(apps):
        struct = {}
        for fap in apps:
            struct[fap] = apps[fap].jsonify()
        redis.set(SchedulerState.KEY_REGISTERED_APP, json.dumps(struct))

    @staticmethod
    def get_available_apps():
        return json.loads(redis.get(SchedulerState.KEY_REGISTERED_APP))


    """ Is scheduller on or off ATM ?"""
    @staticmethod
    def usable():
        val = redis_get(SchedulerState.KEY_USABLE)
        return val == "True"

    @staticmethod
    def set_usable(value):
        redis.set(SchedulerState.KEY_USABLE, str(value))

    @staticmethod
    def default_scheduled_time():
        return redis_get(SchedulerState.KEY_SCHEDULED_APP_TIME)

    """ @staticmethod
    def current_user():
        return redis.hgetall(SchedulerState.KEY_CURRENT_USER)

    @staticmethod
    def set_current_user(user_name):
        now = datetime.datetime.now()
        return redis.hmset(SchedulerState.KEY_CURRENT_USER, {'user_name': user_name,
                                                        'start_at':now,
                                                        'end_at': now+timedelta(seconds=DEFAULT_USER_OCCUPATION)})"""
    @staticmethod
    def get_sunrise():
        v = redis_get(SchedulerState.KEY_SUNRISE, SchedulerState.DEFAULT_RISE)
        return datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def get_sundown():
        v = redis_get(SchedulerState.KEY_SUNDOWN, SchedulerState.DEFAULT_DOWN)
        return datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')

    @staticmethod
    def get_scheduled_apps():
        return redis.lrange(SchedulerState.KEY_SCHEDULED_APP, 0, -1)

    @staticmethod
    def get_current_app():
        return redis.hgetall(SchedulerState.KEY_CURRENT_RUNNING_APP)

    @staticmethod
    def add_schedule_app(app_name):
        apps = SchedulerState.get_scheduled_apps()
        if app_name in apps:
            return
        redis.rpush(SchedulerState.KEY_SCHEDULED_APP, app_name)

    @staticmethod
    def set_app_started_at():
        redis.set(SchedulerState.KEY_APP_STARTED_AT, str(datetime.datetime.now()))

    @staticmethod
    def app_started_at():
        redis.get(SchedulerState.KEY_APP_STARTED_AT)