from __future__ import print_function

import json
import datetime
import sys
import time

from time import sleep
from utils.red import redis, redis_get
from db.models import FappModel, ConfigModel
from db.base import session_factory
from db.tools import to_dict, serialize


def flask_log(msg):
    print(msg, file=sys.stderr)


TASK_EXPIRATION = 60


def add_secs_to_time(timeval, secs_to_add):
    dummy_date = datetime.date(1, 1, 1)
    full_datetime = datetime.datetime.combine(dummy_date, timeval)
    added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
    return added_datetime.time()


class SchedulerState(object):

    DEFAULT_RISE = '2017-07-07T01:00:00'
    DEFAULT_DOWN = '2017-07-07T22:00:00'
    DEFAULT_KEEP_ALIVE_DELAY = 60  # in second
    DEFAULT_USER_OCCUPATION = 120  # in second
    DEFAULT_APP_SCHEDULE_TIME = 15  # in minutes
    KEY_DAY_TABLE = 'frontage_day_table'
    CITY = 'data/bordeaux_user.sun'

    KEY_SUNRISE_OFFSET = 'key_sunrise_offset'
    KEY_SUNDOWN_OFFSET = 'key_sundown_offset'
    KEY_CONNECTED = 'frontage_connected'
    # KEY_APP_START_LOCK = 'key_app_start_lock'
    KEY_USABLE = 'frontage_usable'
    KEY_ENABLE_STATE = 'frontage_enable_state'
    KEY_MODEL = 'frontage_model'
    KEY_SUNRISE = 'frontage_sunrise'
    KEY_SUNDOWN = 'frontage_sundown'
    KEY_FORCED_SUNDOWN_OFFSET = 'key_forced_sundown_offset'
    KEY_FORCED_SUNRISE_OFFSET = 'key_forced_sunrise_offset'
    KEY_SUN_STATE = 'frontage_sunstate'
    KEY_REGISTERED_APP = 'frontage_registered_app'
    KEY_APP_STARTED_AT = 'frontage_app_started_at'
    KEY_NIGHT_START_AT = 'astronomical_twilight_end'
    KEY_NIGHT_END_AT = 'astronomical_twilight_begin'
    KEY_DEFAULT_APP_CURRENT_UUID = 'key_default_app_current_uuid'

    KEY_SCHEDULED_APP_TIME = 'frontage_scheduler_app_time'

    # admin override app
    KEY_FORCED_APP = 'frontage_forced_app'
    # App started by user, (queued)
    KEY_USERS_Q = 'frontage_users_q'

    KEY_CURRENT_RUNNING_APP = 'frontage_current_running_app'
    """KEY_CURRENT_USER = 'frontage_current_user'"""

    @staticmethod
    def get_expires_value():
        session = session_factory()
        expires = session.query(ConfigModel).first()
        session.close()
        if expires:
            return expires.expires_delay
        return TASK_EXPIRATION

    @staticmethod
    def set_expires_value(value=TASK_EXPIRATION):

        session = session_factory()
        app = session.query(ConfigModel).first()
        if not app:
            conf = ConfigModel(expires_delay=value)
            session.add(conf)
            session.commit()
        else:
            app.expires_delay = value

    @staticmethod
    def get_forced_app():
        # add callback on frocer_app_task_launcher to set variable to false
        # when done
        return redis_get(SchedulerState.KEY_FORCED_APP, False) == 'True'

    @staticmethod
    def get_frontage_connected():
        return redis_get(SchedulerState.KEY_CONNECTED, False) == 'True'

    @staticmethod
    def set_frontage_connected(state):
        return redis.set(SchedulerState.KEY_CONNECTED, str(state))

    @staticmethod
    def wait_task_to_start():
        while not SchedulerState.get_current_app():
            sleep(0.1)

    @staticmethod
    def set_forced_app(app_name, params, expires=600):
        from tasks.tasks import start_forced_fap
        from apps.fap import Fap

        SchedulerState.stop_app(SchedulerState.get_current_app(), Fap.CODE_CLOSE_APP, 'The admin started a forced app')
        start_forced_fap.apply_async(
            args=[app_name, 'FORCED', params], expires=expires)

    @staticmethod
    def set_registered_apps(apps):
        # DB
        session = session_factory()
        db_apps = session.query(FappModel).all()
        db_apps_names = [x.name for x in db_apps]

        struct = {}
        for fap in apps:
            struct[fap] = apps[fap].jsonify()
            # not in db ? We create the fapp
            if fap not in db_apps_names:
                db_fap = FappModel(fap, is_scheduled=(not apps[fap].PLAYABLE))
                session.add(db_fap)
        session.commit()
        session.close()
        redis.set(SchedulerState.KEY_REGISTERED_APP, json.dumps(struct))

    @staticmethod
    def get_available_apps():
        return json.loads(redis.get(SchedulerState.KEY_REGISTERED_APP))

    """ Is scheduller on or off ATM ?"""
    @staticmethod
    def usable():
        if not SchedulerState.get_frontage_connected():
            return False

        # FOR TEST ONLY
        # return True
        # -----

        val = redis_get(SchedulerState.KEY_USABLE)
        return val == "True"

    @staticmethod
    def set_usable(value):
        # redis.set(SchedulerState.KEY_USABLE, str(value))
        redis.set(SchedulerState.KEY_USABLE, value)

    @staticmethod
    def set_enable_state(value):
        # redis.set(SchedulerState.KEY_USABLE, str(value))
        if value == 'on':
            SchedulerState.set_usable(True)
        elif value == 'off':
            SchedulerState.set_usable(False)
        redis.set(SchedulerState.KEY_ENABLE_STATE, value)

    @staticmethod
    def get_enable_state():
        # redis.set(SchedulerState.KEY_USABLE, str(value))
        return redis_get(SchedulerState.KEY_ENABLE_STATE, 'on')

    @staticmethod
    def default_scheduled_time():
        return redis_get(SchedulerState.KEY_SCHEDULED_APP_TIME)

    @staticmethod
    def set_sundown(day, at):
        table = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
        table[day][SchedulerState.KEY_NIGHT_START_AT] = day + 'T' + at + ':00'
        dumped = json.dumps(table)

        with open(SchedulerState.CITY, 'w') as f:
            f.write(dumped)
        redis.set(SchedulerState.KEY_DAY_TABLE, dumped)

    @staticmethod
    def set_sunrise(day, at):
        table = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
        table[day][SchedulerState.KEY_NIGHT_END_AT] = day + 'T' + at + ':00'
        dumped = json.dumps(table)

        with open(SchedulerState.CITY, 'w') as f:
            f.write(dumped)

        redis.set(SchedulerState.KEY_DAY_TABLE, dumped)

    # FORCER SUN
    @staticmethod
    def set_forced_sundown(at):
        redis.set(SchedulerState.KEY_FORCED_SUNDOWN_OFFSET, at)

    @staticmethod
    def set_forced_sunrise(at):
        redis.set(SchedulerState.KEY_FORCED_SUNRISE_OFFSET, at)

    @staticmethod
    def get_forced_sundown():
        return redis_get(SchedulerState.KEY_FORCED_SUNDOWN_OFFSET, None)

    @staticmethod
    def get_forced_sunrise():
        return redis_get(SchedulerState.KEY_FORCED_SUNRISE_OFFSET, None)
    # ----

    @staticmethod
    def get_sunrise(at=None):
        # forge date
        # if sundown
        forced_sunrise = SchedulerState.get_forced_sunrise()
        if forced_sunrise:
            try:
                forced_sunrise = datetime.datetime.strptime(forced_sunrise, "%H:%M")
            except ValueError:
                SchedulerState.set_forced_sunrise('')
            else:
                now = datetime.datetime.utcnow()
                forced_sunrise_dt = now.replace(hour=forced_sunrise.hour, minute=forced_sunrise.minute)
                if now > forced_sunrise:
                    forced_sunrise_dt = forced_sunrise_dt + datetime.timedelta(days=1)
                return forced_sunrise_dt
        if not at:
            at = datetime.datetime.now().strftime('%Y-%m-%d')

        v = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))[at].get(
            SchedulerState.KEY_NIGHT_END_AT, SchedulerState.DEFAULT_RISE)
        sunrise = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')

        return sunrise + datetime.timedelta(hours=float(SchedulerState.get_sunrise_offset()))

    @staticmethod
    def get_sundown(at=None):
        forced_sundown = SchedulerState.get_forced_sundown()
        if forced_sundown:
            try:
                forced_sundown = datetime.datetime.strptime(forced_sundown, "%H:%M")
            except ValueError:
                SchedulerState.set_forced_sundown('')
            else:
                now = datetime.datetime.utcnow()
                forced_sundown_dt = now.replace(hour=forced_sundown.hour, minute=forced_sundown.minute)
                if now > forced_sundown:
                    forced_sundown_dt = forced_sundown_dt + datetime.timedelta(days=1)
                return forced_sundown_dt
        if not at:
            at = datetime.datetime.now().strftime('%Y-%m-%d')
        v = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))[at].get(
            SchedulerState.KEY_NIGHT_START_AT, SchedulerState.DEFAULT_DOWN)
        sundown = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
        return sundown + datetime.timedelta(hours=float(SchedulerState.get_sundown_offset()))

    @staticmethod
    def get_current_app():
        return json.loads(redis.get(SchedulerState.KEY_CURRENT_RUNNING_APP))

    @staticmethod
    def set_current_app(app_struct):
        redis.set(
            SchedulerState.KEY_CURRENT_RUNNING_APP,
            json.dumps(app_struct))

    @staticmethod
    def set_sundown_offset(offset=0):
        redis.set(SchedulerState.KEY_SUNDOWN_OFFSET, offset)
        redis.set(SchedulerState.KEY_FORCED_SUNDOWN_OFFSET, 0)
        return True

    @staticmethod
    def get_sundown_offset():
        return redis_get(SchedulerState.KEY_SUNDOWN_OFFSET, 0)

    @staticmethod
    def set_sunrise_offset(offset=0):
        redis.set(SchedulerState.KEY_SUNRISE_OFFSET, offset)
        redis.set(SchedulerState.KEY_FORCED_SUNRISE_OFFSET, 0)
        return True

    @staticmethod
    def get_sunrise_offset():
        return redis_get(SchedulerState.KEY_SUNRISE_OFFSET, 0)

    # ============= DEFAULT SCHEDULED APP
    @staticmethod
    def get_next_default_app():
        # default_app = redis_get(SchedulerState.KEY_DEFAULT_APP_CURRENT_UUID, b"").decode('utf8')
        default_app = redis_get(SchedulerState.KEY_DEFAULT_APP_CURRENT_UUID, "")
        select_next = True
        apps = SchedulerState.get_default_scheduled_app(serialized=False, todict=False)
        if not apps:
            return None
        for app in apps:
            if select_next:
                redis.set(SchedulerState.KEY_DEFAULT_APP_CURRENT_UUID, app.uniqid)
                return app
            if app.uniqid == default_app:
                select_next = True

        redis.set(SchedulerState.KEY_DEFAULT_APP_CURRENT_UUID, apps[0].uniqid)
        return apps[0]

    @staticmethod
    def set_default_scheduled_app_state(app_name, state):
        if app_name not in SchedulerState.get_available_apps():
            raise ValueError('Bad Name')

        session = session_factory()
        app = session.query(FappModel).filter_by(name=app_name).first()
        if not app:
            fap = FappModel(app_name, is_scheduled=state)
            session.add(fap)
            session.commit()
        else:
            app.is_scheduled = state
            session.commit()
        session.close()

    @staticmethod
    def get_default_scheduled_app(serialized=False, todict=True):
        # Get model form DB
        apps = []
        session = session_factory()
        for f in session.query(FappModel).filter_by(is_scheduled=True).all():
            if serialized:
                apps.append(serialize(to_dict(f)))
            else:
                if todict:
                    apps.append(to_dict(f))
                else:
                    if f.default_params:
                        f.default_params = json.loads(f.default_params)
                    apps.append(f)
        session.close()
        return apps

    @staticmethod
    def set_default_scheduled_app_params(app_name, app_params):
        if not app_params:
            app_params = None
        try:
            session = session_factory()
            fap = session.query(FappModel).filter_by(name=app_name).first()
            if not fap:
                return False
            fap.default_params = app_params
            session.commit()
        finally:
            session.close()

        return True

    @staticmethod
    def get_default_scheduled_app_params(app_name, serialized=True):
        try:
            session = session_factory()
            fap = session.query(FappModel).filter_by(name=app_name).first()
            if not fap:
                return False

            fap_dict = to_dict(fap)
            if serialize:
                return serialize(fap_dict)
            else:
                return fap_dict
        finally:
            session.close()

    # =============
    @staticmethod
    def set_app_started_at():
        redis.set(
            SchedulerState.KEY_APP_STARTED_AT,
            datetime.datetime.now().isoformat())

    @staticmethod
    def app_started_at():
        redis.get(SchedulerState.KEY_APP_STARTED_AT)

    @staticmethod
    def stop_app(c_app, stop_code=None, stop_message=None):
        flask_log(" ========= STOP_APP ====================")
        if not c_app:
            return

        from tasks.celery import app
        # Websock.send_data(stop_code, stop_message)
        # revoke(c_app['task_id'], terminate=True, signal='SIGUSR1')
        # app.control.revoke(c_app['task_id'], terminate=True, signal='SIGUSR1')
        app.control.revoke(c_app['task_id'], terminate=True)
        sleep(0.05)

    @staticmethod
    def pop_user_app_queue(queue=None):
        if not queue:
            queue = SchedulerState.get_user_app_queue()
        p = queue.pop(0)
        redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
        return p

    @staticmethod
    def clear_user_app_queue():
        redis.set(SchedulerState.KEY_USERS_Q, '[]')

    @staticmethod
    def get_user_app_queue():
        return SchedulerState.get_user_queue()
        # from tasks.celery import app
        # return
        # app.control.inspect(['celery@workerqueue']).reserved()['celery@workerqueue']

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
            if datetime.datetime.now() <= datetime.datetime.strptime(
                    c_app['expire_at'], "%Y-%m-%d %H:%M:%S.%f"):
                raise Exception('User is already the owner of the current app')

        app_struct = {'name': app_name,
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

        return {
            'keep_alive_delay': SchedulerState.DEFAULT_KEEP_ALIVE_DELAY,
            'queued': True}

    # redis.rpush(SchedulerState.KEY_SCHEDULED_APP, app_name)
    # return redis.lrange(SchedulerState.KEY_SCHEDULED_APP, 0, -1)
