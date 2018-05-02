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
from utils.websock import Websock


def flask_log(msg):
    print(msg, file=sys.stderr)


def add_secs_to_time(timeval, secs_to_add):
    dummy_date = datetime.date(1, 1, 1)
    full_datetime = datetime.datetime.combine(dummy_date, timeval)
    added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
    return added_datetime.time()


class SchedulerState(object):

    DEFAULT_KEEP_ALIVE_DELAY = 60  # in second
    KEY_DAY_TABLE = 'frontage_day_table'
    CITY = 'data/bordeaux_user.sun'

    KEY_SUNRISE_OFFSET = 'key_sunrise_offset'
    KEY_SUNDOWN_OFFSET = 'key_sundown_offset'
    # KEY_APP_START_LOCK = 'key_app_start_lock'
    KEY_USABLE = 'frontage_usable'
    KEY_ENABLE_STATE = 'frontage_enable_state'
    KEY_MODEL = 'frontage_model'
    KEY_FRONTAGE_ON_OFF = 'key_frontage_on_off'
    KEY_NOTICE_EXPIRE_SOON = 'key_notice_expire_soon'
    KEY_NOTICE_EXPIRE = 'key_notice_expire'
    KEY_SUN_STATE = 'frontage_sunstate'
    KEY_REGISTERED_APP = 'frontage_registered_app'
    KEY_EVENT_LOCK = 'key_event_lock'
    KEY_APP_STARTED_AT = 'frontage_app_started_at'
    KEY_ON_TIME = 'astronomical_twilight_end'
    KEY_OFF_TIME = 'astronomical_twilight_begin'
    KEY_DEFAULT_APP_CURRENT_INDEX = 'key_default_app_current_index'

    # admin override app
    KEY_FORCED_APP = 'frontage_forced_app'
    # App started by user, (queued)
    KEY_USERS_Q = 'frontage_users_q'

    KEY_CURRENT_RUNNING_APP = 'frontage_current_running_app'
    """KEY_CURRENT_USER = 'frontage_current_user'"""

    @staticmethod
    def get_expires_value():
        session = session_factory()
        expires = session.query(ConfigModel).first().expires_delay
        session.close()
        return expires

    @staticmethod
    def get_default_fap_lifetime():
        session = session_factory()
        lifetime = session.query(ConfigModel).first().default_app_lifetime
        session.close()
        return lifetime

    @staticmethod
    def set_expires_value(value):
        session = session_factory()
        app = session.query(ConfigModel).first()
        if not app:
            conf = ConfigModel()
            session.add(conf)
        else:
            app.expires_delay = value
        session.commit()
        session.close()

    @staticmethod
    def set_default_fap_lifetime(value):
        session = session_factory()
        app = session.query(ConfigModel).first()
        if not app:
            conf = ConfigModel()
            session.add(conf)
        else:
            app.default_app_lifetime = max(5, int(value))
        session.commit()
        session.close()

    @staticmethod
    def set_expire_soon(value=True):
        flask_log('==== Set Expire Soon')
        redis.set(SchedulerState.KEY_NOTICE_EXPIRE_SOON, value)

    @staticmethod
    def set_expire(value=True):
        redis.set(SchedulerState.KEY_NOTICE_EXPIRE, value)

    @staticmethod
    def get_expire():
        return redis_get(SchedulerState.KEY_NOTICE_EXPIRE, False) == 'True'

    @staticmethod
    def get_expire_soon():
        return redis_get(SchedulerState.KEY_NOTICE_EXPIRE_SOON, False) == 'True'

    @staticmethod
    def get_forced_app():
        return redis_get(SchedulerState.KEY_FORCED_APP, False) == 'True'

    @staticmethod
    def wait_task_to_start():
        while not SchedulerState.get_current_app():
            sleep(0.1)

    @staticmethod
    def set_forced_app(app_name, params, expires=600):
        from tasks.tasks import start_forced_fap
        # from apps.fap import Fap
        if SchedulerState.get_forced_app():
            return False
        # TODO is a lock necessary here?
        SchedulerState.stop_app(SchedulerState.get_current_app(), 1, 'The admin started a forced app')
        start_forced_fap.apply_async(args=[app_name, 'FORCED', params], expires=expires)
        redis.set(SchedulerState.KEY_FORCED_APP, 'True')
        return True

    @staticmethod
    def stop_forced_app():
        from apps.fap import Fap
        if SchedulerState.get_forced_app():
            SchedulerState.stop_app(SchedulerState.get_current_app(), Fap.CODE_CLOSE_APP, 'App unforced')
            redis.set(SchedulerState.KEY_FORCED_APP, 'False')
            return True
        return False

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

    def set_frontage_on(value):
        redis.set(SchedulerState.KEY_FRONTAGE_ON_OFF, value)

    @staticmethod
    def is_frontage_on():
        val = redis_get(SchedulerState.KEY_FRONTAGE_ON_OFF)
        return val == "True"

    """ Is scheduller on or off ATM ?"""
    @staticmethod
    def usable():
        val = redis_get(SchedulerState.KEY_USABLE)
        return val == "True"

    @staticmethod
    def set_usable(value):
        # redis.set(SchedulerState.KEY_USABLE, str(value))
        redis.set(SchedulerState.KEY_USABLE, value)

    @staticmethod
    def set_enable_state(value):
        # redis.set(SchedulerState.KEY_USABLE, str(value))
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.state = value
        session.commit()
        session.close()

        # if value == 'on':
        #     SchedulerState.set_frontage_on(True)
        # elif value == 'off':
        #     SchedulerState.set_frontage_on(False)
        # redis.set(SchedulerState.KEY_ENABLE_STATE, value)

    @staticmethod
    def get_enable_state():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.state
        session.close()
        return val
        # redis.set(SchedulerState.KEY_USABLE, str(value))
        # return redis_get(SchedulerState.KEY_ENABLE_STATE, 'on')

    @staticmethod
    def set_sundown(day, at):
        table = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
        table[day][SchedulerState.KEY_ON_TIME] = day + 'T' + at + ':00'
        dumped = json.dumps(table)

        with open(SchedulerState.CITY, 'w') as f:
            f.write(dumped)
        redis.set(SchedulerState.KEY_DAY_TABLE, dumped)

    @staticmethod
    def set_sunrise(day, at):
        table = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
        table[day][SchedulerState.KEY_OFF_TIME] = day + 'T' + at + ':00'
        dumped = json.dumps(table)

        with open(SchedulerState.CITY, 'w') as f:
            f.write(dumped)

        redis.set(SchedulerState.KEY_DAY_TABLE, dumped)

    @staticmethod
    def set_forced_on_time(at):
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.forced_sunset = at
        conf.offset_sunset = 0
        session.commit()
        session.close()

    @staticmethod
    def set_forced_off_time(at):
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.forced_sunrise = at
        conf.offset_sunrise = 0
        session.commit()
        session.close()

    @staticmethod
    def get_forced_on_time():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.forced_sunset
        session.close()
        return val

    @staticmethod
    def get_forced_off_time():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.forced_sunrise
        session.close()
        return val
    # ----

    @staticmethod
    def get_scheduled_off_time():
        forced_off_time = SchedulerState.get_forced_off_time()
        if forced_off_time:
            try:
                forced_off_time = datetime.datetime.strptime(forced_off_time, "%H:%M")
            except ValueError:
                SchedulerState.set_forced_off_time('')
            else:
                now = datetime.datetime.now()
                forced_sunrise_dt = now.replace(hour=forced_off_time.hour, minute=forced_off_time.minute,
                                                second=0, microsecond=0)
                return forced_sunrise_dt
        at = datetime.datetime.now().strftime('%Y-%m-%d')
        v = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))[at].get(
            SchedulerState.KEY_OFF_TIME, datetime.datetime.now().isoformat())
        sunrise = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')

        return sunrise + datetime.timedelta(hours=float(SchedulerState.get_sunrise_offset()))

    @staticmethod
    def get_scheduled_on_time():
        forced_on_time = SchedulerState.get_forced_on_time()
        if forced_on_time:
            try:
                forced_on_time = datetime.datetime.strptime(forced_on_time, "%H:%M")
            except ValueError:
                SchedulerState.set_forced_on_time('')
            else:
                now = datetime.datetime.now()
                forced_sundown_dt = now.replace(hour=forced_on_time.hour, minute=forced_on_time.minute,
                                                second=0, microsecond=0)
                return forced_sundown_dt
        at = datetime.datetime.now().strftime('%Y-%m-%d')
        v = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))[at].get(
            SchedulerState.KEY_ON_TIME, datetime.datetime.now().isoformat())
        sunset = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
        return sunset + datetime.timedelta(hours=float(SchedulerState.get_sundown_offset()))

    @staticmethod
    def get_current_app():
        return json.loads(redis.get(SchedulerState.KEY_CURRENT_RUNNING_APP))

    @staticmethod
    def set_current_app(app_struct):
        redis.set(
            SchedulerState.KEY_CURRENT_RUNNING_APP,
            json.dumps(app_struct))

    @staticmethod
    def set_sunset_offset(offset=0):
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.forced_sunset = ""
        conf.offset_sunset = offset
        session.commit()
        session.close()
        # return val

        # redis.set(SchedulerState.KEY_SUNDOWN_OFFSET, offset)
        # redis.set(SchedulerState.KEY_FORCED_SUNDOWN_OFFSET, 0)
        # return True

    @staticmethod
    def get_sundown_offset():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        offset = conf.offset_sunset
        session.close()

        return offset
        # return redis_get(SchedulerState.KEY_SUNDOWN_OFFSET, 0)

    @staticmethod
    def set_sunrise_offset(offset=0):
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.forced_sunrise = ""
        conf.offset_sunrise = offset
        session.commit()
        session.close()
        # redis.set(SchedulerState.KEY_SUNRISE_OFFSET, offset)
        # redis.set(SchedulerState.KEY_FORCED_SUNRISE_OFFSET, 0)
        # return True

    @staticmethod
    def get_sunrise_offset():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        offset = conf.offset_sunrise
        session.close()

        return offset
        # return redis_get(SchedulerState.KEY_SUNRISE_OFFSET, 0)

    # ============= DEFAULT SCHEDULED APP
    @staticmethod
    def get_next_default_app():
        index = int(redis_get(SchedulerState.KEY_DEFAULT_APP_CURRENT_INDEX, 0))
        apps = SchedulerState.get_default_scheduled_apps()
        try:
            app = apps[index]
        except IndexError:
            return None
        index = (index + 1) % len(apps)
        redis.set(SchedulerState.KEY_DEFAULT_APP_CURRENT_INDEX, index)
        return app

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
    def get_default_scheduled_apps(serialized=False):
        # Get model form DB
        apps = []
        session = session_factory()
        for f in session.query(FappModel).filter_by(is_scheduled=True).all():
            if serialized:
                apps.append(serialize(to_dict(f)))
            else:
                app = to_dict(f)
                app['default_params'] = json.loads(app['default_params'])
                apps.append(app)

        session.close()
        return apps

    @staticmethod
    def set_default_scheduled_app_params(app_name, app_params):
        if not app_params:
            app_params = None
        elif isinstance(app_params, dict):
            app_params = json.dumps(app_params)

        session = session_factory()
        try:
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
        session = session_factory()
        try:
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
        # flask_log(" ========= STOP_APP ====================")
        if not c_app:
            return

        from tasks.celery import app
        if not c_app.get('is_default', False):
            if stop_code and stop_message:
                Websock.send_data(stop_code, stop_message, c_app['username'])

        sleep(0.1)
        # revoke(c_app['task_id'], terminate=True, signal='SIGUSR1')
        # app.control.revoke(c_app['task_id'], terminate=True, signal='SIGUSR1')
        app.control.revoke(c_app['task_id'], terminate=True)
        sleep(0.05)

    @staticmethod
    def pop_user_app_queue(queue=None):
        if not queue:
            queue = SchedulerState.get_user_app_queue()
        if not queue:
            return
        p = queue.pop(0)
        redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
        return p

    @staticmethod
    def set_event_lock(val):
        redis.set(SchedulerState.KEY_EVENT_LOCK, val)

    @staticmethod
    def is_event_lock():
        return redis_get(SchedulerState.KEY_EVENT_LOCK, 'False') == 'True'

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
