from __future__ import print_function

import json
import datetime
import sys
import time

from time import sleep
from celery.task.control import revoke
from utils.red import redis, redis_get

def flask_log(msg):
    print(msg, file=sys.stderr)



class SchedulerState(object):

    DEFAULT_RISE = '2017-07-07T01:00:00'
    DEFAULT_DOWN = '2017-07-07T22:00:00'
    DEFAULT_KEEP_ALIVE_DELAY = 60  # in second
    DEFAULT_USER_OCCUPATION = 120  # in second
    DEFAULT_APP_SCHEDULE_TIME = 15  # in minutes
    KEY_DAY_TABLE = 'frontage_day_table'
    CITY = 'data/bordeaux_user.sun'

    KEY_USABLE = 'frontage_usable'
    KEY_MODEL = 'frontage_model'
    KEY_SUNRISE = 'frontage_sunrise'
    KEY_SUNDOWN = 'frontage_sundown'
    KEY_SUN_STATE = 'frontage_sunstate'
    KEY_REGISTERED_APP = 'frontage_registered_app'
    KEY_APP_STARTED_AT = 'frontage_app_started_at'
    KEY_NIGHT_START_AT = 'astronomical_twilight_end'
    KEY_NIGHT_END_AT = 'astronomical_twilight_begin'

    KEY_SCHEDULED_APP_TIME = 'frontage_scheduler_app_time'

    # admin override app
    KEY_FORCED_APP = 'frontage_forced_app'
    # App started by user, (queued)
    KEY_USERS_Q = 'frontage_users_q'

    KEY_CURRENT_RUNNING_APP = 'frontage_current_running_app'
    """KEY_CURRENT_USER = 'frontage_current_user'"""

    @staticmethod
    def get_forced_app():
        # add callback on frocer_app_task_launcher to set variable to false when done
        return redis_get(SchedulerState.KEY_FORCED_APP, False) == 'True'

    @staticmethod
    def set_forced_app(app_name, params, expires=600):
        from tasks.tasks import start_forced_fap, clear_all_task
        clear_all_task()
        t = start_forced_fap.apply_async(args=[app_name, 'FORCED', params], expires=expires)


    @staticmethod
    def set_registered_apps(apps):
        struct = {}
        for fap in apps:
            print('*******************+++')
            print(apps[fap].PARAMS_LIST)
            print(apps[fap].jsonify())
            print('*******************')
            struct[fap] = apps[fap].jsonify()
        redis.set(SchedulerState.KEY_REGISTERED_APP, json.dumps(struct))

    @staticmethod
    def get_available_apps():
        return json.loads(redis.get(SchedulerState.KEY_REGISTERED_APP))


    """ Is scheduller on or off ATM ?"""
    @staticmethod
    def usable():

        return True

        val = redis_get(SchedulerState.KEY_USABLE)
        return val == "True"

    @staticmethod
    def set_usable(value):
        ##### redis.set(SchedulerState.KEY_USABLE, str(value))
        redis.set(SchedulerState.KEY_USABLE, str('True'))

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
    def set_sundown(day, at):
        table = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
        table[day][SchedulerState.KEY_NIGHT_START_AT] = day+'T'+at+':00'
        dumped = json.dumps(table)

        with open(SchedulerState.CITY, 'w') as f:
            f.write(dumped)
        redis.set(SchedulerState.KEY_DAY_TABLE, dumped)

    @staticmethod
    def set_sunrise(day, at):
        table = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
        table[day][SchedulerState.KEY_NIGHT_END_AT] = day+'T'+at+':00'
        dumped = json.dumps(table)

        with open(SchedulerState.CITY, 'w') as f:
            f.write(dumped)

        redis.set(SchedulerState.KEY_DAY_TABLE, dumped)

    @staticmethod
    def get_sunrise(at=None):
        if not at:
            at = datetime.datetime.now().strftime('%Y-%m-%d')

        v = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))[at].get(SchedulerState.KEY_NIGHT_END_AT, SchedulerState.DEFAULT_RISE)
        return datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def get_sundown(at=None):
        if not at:
            at = datetime.datetime.now().strftime('%Y-%m-%d')

        v = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))[at].get(SchedulerState.KEY_NIGHT_START_AT, SchedulerState.DEFAULT_DOWN)
        return datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def get_current_app():
        return json.loads(redis.get(SchedulerState.KEY_CURRENT_RUNNING_APP))

    @staticmethod
    def set_current_app(app_struct):
        redis.set(SchedulerState.KEY_CURRENT_RUNNING_APP, json.dumps(app_struct))

    @staticmethod
    def set_app_started_at():
        redis.set(SchedulerState.KEY_APP_STARTED_AT, datetime.datetime.now().isoformat())

    @staticmethod
    def app_started_at():
        redis.get(SchedulerState.KEY_APP_STARTED_AT)

    @staticmethod
    def stop_app(c_app):
        revoke(c_app['task_id'], terminate=True)
        sleep(0.05)

    @staticmethod
    def pop_user_app_queue(queue=None):
        if not queue:
            queue = SchedulerState.get_user_app_queue()
        p = queue.pop(0)
        redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
        return p

    @staticmethod
    def get_user_app_queue():
        return SchedulerState.get_user_queue()
        # from tasks.celery import app
        # return app.control.inspect(['celery@workerqueue']).reserved()['celery@workerqueue']

    @staticmethod
    def get_user_position(user):
        queue = SchedulerState.get_user_queue()
        i = 1
        username = user['username']
        for u in queue:
            if u['username'] == username:
                u['last_alive'] = time.time()
                redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
                return i
            i += 1
        return -1

    @staticmethod
    def remove_user_position(user):
        queue = SchedulerState.get_user_queue()
        username = user['username']
        for u in list(queue):
            if u['username'] == username:
                queue.remove(u)
                redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
                return True
        return False


    @staticmethod
    def get_user_queue():
        return json.loads(redis_get(SchedulerState.KEY_USERS_Q, '[]'))

    @staticmethod
    def start_scheduled_app(username, app_name, params, expires):
        # from tasks.tasks import start_fap
        # Check Queue
        queue = SchedulerState.get_user_queue()
        if next((x for x in queue if x['username'] == username), False):
            raise Exception('User already in queue')
        c_app = SchedulerState.get_current_app()
        if c_app and c_app.get('username', False) == username:
            if datetime.datetime.now() <= datetime.datetime.strptime(c_app['expire_at'], "%Y-%m-%d %H:%M:%S.%f"):
                raise Exception('User is already the owner of the current app')

        app_struct = {  'name': app_name,
                    'username': username,
                    'params': params,
                    'started_wait_at': datetime.datetime.now().isoformat(),
                    'expires': expires,
                    'task_id': None,
                    'last_alive': time.time(),
                    'expire_at': None}
        # Actually starting app
        # t = start_fap.apply_async(args=[app_name, username, params, expires], queue='userapp', potato='fghbjndfghj')
        # Add to queue starting app
        queue.append(app_struct)
        redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))

        return {'keep_alive_delay': SchedulerState.DEFAULT_KEEP_ALIVE_DELAY, 'queued': True}


    # redis.rpush(SchedulerState.KEY_SCHEDULED_APP, app_name)
    # return redis.lrange(SchedulerState.KEY_SCHEDULED_APP, 0, -1)