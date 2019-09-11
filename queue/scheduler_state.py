import json
import logging
import datetime
import time

from time import sleep
from utils.red import redis, redis_get
from db.models import FappModel, ConfigModel, DimensionsModel, CellTableModel
from db.base import session_factory, engine
from db.tools import to_dict, serialize

def add_secs_to_time(timeval, secs_to_add):
    dummy_date = datetime.date(1, 1, 1)
    full_datetime = datetime.datetime.combine(dummy_date, timeval)
    added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
    return added_datetime.time()


class SchedulerState(object):

    DEFAULT_KEEP_ALIVE_DELAY = 60  # in second
    DEFAULT_CURRENT_APP_KEEP_ALIVE_DELAY = 15  # in second
    KEY_DAY_TABLE = 'frontage_day_table'
    CITY = 'data/sun/bordeaux.json'

    # KEY_APP_START_LOCK = 'key_app_start_lock'
    KEY_USABLE = 'frontage_usable'
    KEY_GEOMETRY = 'frontage_geometry'
    KEY_ENABLE_STATE = 'frontage_enable_state'
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
    KEY_SET_DEFAULT_DRAWING = 'key_set_default_drawing'

    # admin override app
    KEY_FORCED_APP = 'frontage_forced_app'
    KEY_STOP_APP_REQUEST = 'frontage_stop_app_request'
    KEY_FORCED_APP_REQUEST = 'frontage_forced_app_request'
    # App started by user, (queued)
    KEY_USERS_Q = 'frontage_users_q'

    KEY_CURRENT_RUNNING_APP = 'frontage_current_running_app'

    @staticmethod
    def get_rows():
        session = session_factory()
        rows = session.query(DimensionsModel).first().rows
        session.close()
        return rows

    @staticmethod
    def get_cols():
        session = session_factory()
        cols = session.query(DimensionsModel).first().cols
        session.close()
        return cols

    @staticmethod
    def get_amount():
        session = session_factory()
        amount = session.query(DimensionsModel).first().amount
        session.close()
        return amount

    @staticmethod
    def get_initialised():
        session = session_factory()
        initialised = session.query(DimensionsModel).first().initialised
        session.close()
        return initialised

    @staticmethod
    def get_disabled():
        return []
        session = session_factory()
        pixels = SchedulerState.get_pixels_dic()
        rows = SchedulerState.get_rows()
        cols = SchedulerState.get_cols()
        model = [[ False for i in range(cols)] for j in range(rows)]
        for pixel in pixels.values() :
            ((x,y), ind) = pixel
            if( x < rows and y < cols):
                model[x][y] = True
        disabled = []
        for i in range(rows):
            for j in range(cols):
                if (not model[i][j]) :
                    disabled += [[i,j]]
        return disabled

    @staticmethod
    def set_rows(value):
        session = session_factory()
        conf = session.query(DimensionsModel).first()
        conf.rows = value
        session.commit()
        session.close()

    @staticmethod
    def set_cols(value):
        session = session_factory()
        conf = session.query(DimensionsModel).first()
        conf.cols = value
        session.commit()
        session.close()

    @staticmethod
    def set_amount(value):
        session = session_factory()
        conf = session.query(DimensionsModel).first()
        conf.amount = value
        session.commit()
        session.close()

    @staticmethod
    def set_initialised(value):
        session = session_factory()
        conf = session.query(DimensionsModel).first()
        conf.initialised = value
        session.commit()
        session.close()

    @staticmethod
    def update_geometry(r=None, c=None, d=None):
        redis.set(SchedulerState.KEY_GEOMETRY, json.dumps({'rows': r,
                                                           'cols': c,
                                                           'disabled': d}))

    @staticmethod
    def add_cell(x, y, mac_address, ind):
        logging.info("Considering {0} at (({1}, {2}), {3})".format(mac_address, x, y, ind))
        session = session_factory()
        table = session.query(CellTableModel).all()
        isInTable = False
        for cell in table:
            if (cell.X == x and cell.Y == y):
                logging.info("Found its position : updating mac and ind...")
                isInTable = True
                cell.MacAddress = mac_address
                cell.Ind = ind
            elif (cell.MacAddress == mac_address) :
                logging.info("Found its mac : updating position and ind...")
                isInTable = True
                cell.Ind = ind
                cell.X == x
                cell.Y == y
        if (isInTable == False):
            logging.error("Not found : adding to table")
            cell = CellTableModel(x, y, mac_address, ind)
            session.add(cell)
            session.commit()

        session.close()

    @staticmethod
    def get_pixels_dic() :
        session = session_factory()
        table = session.query(CellTableModel).all()
        dic = {}
        for cell in table :
            dic[cell.MacAddress] = ((cell.X, cell.Y), cell.Ind)
        session.close()
        return dic

    @staticmethod
    def drop_dic() :
        session = session_factory()
        table = session.query(CellTableModel).all()
        for cell in table :
            session.delete(cell)
        session.commit()
        session.close()

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
        conf = session.query(ConfigModel).first()
        conf.expires_delay = value
        session.commit()
        session.close()

    @staticmethod
    def set_default_fap_lifetime(value):
        session = session_factory()
        config = session.query(ConfigModel).first()
        config.default_app_lifetime = max(5, int(value))
        session.commit()
        session.close()

    @staticmethod
    def set_expire_soon(value=True):
        redis.set(SchedulerState.KEY_NOTICE_EXPIRE_SOON, str(value))

    @staticmethod
    def set_expire(value=True):
        redis.set(SchedulerState.KEY_NOTICE_EXPIRE, str(value))

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
    def get_close_app_request():
        # Return (boolean, userid) = has a request been initiated? If yes, by who?
        request = json.loads(redis_get(SchedulerState.KEY_STOP_APP_REQUEST, '{}'))
        if 'userid' in request:
            return True, request['userid']
        return False, None

    @staticmethod
    def get_default_drawing_request():
        # Return true if a request has been initiated to set the current drawing as the default
        request = redis_get(SchedulerState.KEY_SET_DEFAULT_DRAWING, False) == 'True'
        redis.set(SchedulerState.KEY_SET_DEFAULT_DRAWING, 'False')
        return request

    @staticmethod
    def get_forced_app_request():
        return json.loads(redis_get(SchedulerState.KEY_FORCED_APP_REQUEST, '{}'))

    @staticmethod
    def clear_forced_app_request():
        redis.set(SchedulerState.KEY_FORCED_APP_REQUEST, '{}')

    @staticmethod
    def wait_task_to_start():
        while not SchedulerState.get_current_app():
            sleep(0.1)

    @staticmethod
    def set_forced_app_request(app_name, params):
        # from apps.fap import Fap
        if SchedulerState.get_forced_app():
            return False

        redis.set(SchedulerState.KEY_FORCED_APP_REQUEST, json.dumps({'name': app_name, 'params': params}))
        return True

    @staticmethod
    def stop_forced_app_request(user):
        if not SchedulerState.get_forced_app():
            return False
        else:
            SchedulerState.stop_app_request(user)
            return True

    @staticmethod
    def set_registered_apps(apps):
        struct = {}
        for fap in apps:
            struct[fap] = apps[fap].jsonify()
        redis.set(SchedulerState.KEY_REGISTERED_APP, json.dumps(struct))

    @staticmethod
    def set_default_drawing():
        c_app = SchedulerState.get_current_app()
        if('name' in c_app and c_app['name'] == "Drawing"):
            redis.set(SchedulerState.KEY_SET_DEFAULT_DRAWING, "True")
            return True
        return False

    @staticmethod
    def get_available_apps():
        return json.loads(redis.get(SchedulerState.KEY_REGISTERED_APP))

    @staticmethod
    def set_frontage_on(value):
        redis.set(SchedulerState.KEY_FRONTAGE_ON_OFF, str(value))

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
        redis.set(SchedulerState.KEY_USABLE, str(value))

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

    @staticmethod
    def get_time_on():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.time_on
        session.close()
        return val

    @staticmethod
    def get_time_off():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.time_off
        session.close()
        return val

    @staticmethod
    def get_offset_time_on():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.offset_time_on
        session.close()
        return val

    @staticmethod
    def get_offset_time_off():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        val = conf.offset_time_off
        session.close()
        return val

    @staticmethod
    def set_time_on(at):
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.time_on = at
        if conf.time_on not in ['sunrise', 'sunset']:
            conf.offset_time_on = 0
        session.commit()
        session.close()

    @staticmethod
    def set_time_off(at):
        session = session_factory()
        conf = session.query(ConfigModel).first()
        conf.time_off = at
        if conf.time_off not in ['sunrise', 'sunset']:
            conf.offset_time_off = 0
        session.commit()
        session.close()

    @staticmethod
    def set_offset_time_off(offset=0):
        if isinstance(offset, int):
            session = session_factory()
            conf = session.query(ConfigModel).first()
            conf.offset_time_off = offset
            session.commit()
            session.close()

    @staticmethod
    def set_offset_time_on(offset=0):
        if isinstance(offset, int):
            session = session_factory()
            conf = session.query(ConfigModel).first()
            conf.offset_time_on = offset
            session.commit()
            session.close()

    @staticmethod
    def _get_scheduled_off_time():
        time_off = SchedulerState.get_time_off()
        now = datetime.datetime.now()

        if time_off in ['sunrise', 'sunset']:
            at = now.strftime('%Y-%m-%d')
            calendar = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
            if calendar and at in calendar:
                v = calendar[at].get(SchedulerState.KEY_OFF_TIME if time_off=='sunrise' else SchedulerState.KEY_ON_TIME, now.isoformat())
                off_time = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
                return off_time + datetime.timedelta(seconds=float(SchedulerState.get_offset_time_off()))
        else:
            # Other values of time_off can be "%H:%M"
            try:
                formatted_time_off = datetime.datetime.strptime(time_off, "%H:%M")
            except ValueError:
                SchedulerState.set_time_off('23:00')
            else:
                return now.replace(hour=formatted_time_off.hour, minute=formatted_time_off.minute, second=0, microsecond=0)

        # Sanity check: worst case: off time is unknown, return past date
        return now + datetime.timedelta(hours=-10)

    @staticmethod
    def get_scheduled_off_time():
        off_time = SchedulerState._get_scheduled_off_time()
        on_time = SchedulerState._get_scheduled_on_time()
        now = datetime.datetime.now()

        if on_time > off_time and now > off_time:
            off_time = off_time + datetime.timedelta(days=1)
        return off_time

    @staticmethod
    def get_scheduled_on_time():
        off_time = SchedulerState._get_scheduled_off_time()
        on_time = SchedulerState._get_scheduled_on_time()
        now = datetime.datetime.now()

        if on_time > off_time and now < off_time:
            on_time = on_time + datetime.timedelta(days=-1)
        return on_time

    @staticmethod
    def _get_scheduled_on_time():
        time_on = SchedulerState.get_time_on()
        now = datetime.datetime.now()

        if time_on in ['sunrise', 'sunset']:
            at = now.strftime('%Y-%m-%d')
            calendar = json.loads(redis.get(SchedulerState.KEY_DAY_TABLE))
            if calendar and at in calendar:
                v = calendar[at].get(SchedulerState.KEY_OFF_TIME if time_on=='sunrise' else SchedulerState.KEY_ON_TIME, now.isoformat())
                on_time = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
                return on_time + datetime.timedelta(seconds=float(SchedulerState.get_offset_time_on()))
        else:
            # Other values of time_on can be "%H:%M"
            try:
                formatted_time_on = datetime.datetime.strptime(time_on, "%H:%M")
            except ValueError:
                SchedulerState.set_time_on('20:00')
            else:
                return now.replace(hour=formatted_time_on.hour, minute=formatted_time_on.minute, second=0, microsecond=0)

        # Sanity check: worst case: on time is unknown, return future date
        return now + datetime.timedelta(hours=10)

    @staticmethod
    def get_current_app():
        c_app = redis.get(SchedulerState.KEY_CURRENT_RUNNING_APP)
        return json.loads(c_app) if c_app is not None else None

    @staticmethod
    def set_current_app(app_struct):
        redis.set(
            SchedulerState.KEY_CURRENT_RUNNING_APP,
            json.dumps(app_struct))

    @staticmethod
    def get_admin_credentials():
        session = session_factory()
        conf = session.query(ConfigModel).first()
        login = conf.admin_login
        hash = conf.admin_hash
        session.close()
        return login, hash

    # ============= DEFAULT SCHEDULED APP
    @staticmethod
    def get_next_default_app():
        apps = SchedulerState.get_default_scheduled_apps()
        num_apps = len(apps)

        if num_apps == 0:
            return None

        index = int(redis_get(SchedulerState.KEY_DEFAULT_APP_CURRENT_INDEX, 0))
        index = (index + 1) % num_apps
        redis.set(SchedulerState.KEY_DEFAULT_APP_CURRENT_INDEX, index)

        try:
            app = apps[index]
        except IndexError:
            return None
        else:
            return app

    @staticmethod
    def set_default_scheduled_app_state(app_name, state):
        if app_name not in SchedulerState.get_available_apps():
            raise ValueError('Bad Name')

        session = session_factory()
        app = session.query(FappModel).filter_by(name=app_name).first()
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
    def stop_app_request(user):
        # Store the user who initiated the request
        redis.set(SchedulerState.KEY_STOP_APP_REQUEST, json.dumps(user))

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
        redis.set(SchedulerState.KEY_EVENT_LOCK, str(val))

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
        userid = user['userid']
        for u in queue:
            if u['userid'] == userid:
                u['last_alive'] = time.time()
                redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
                return i
            i += 1
        return -1

    @staticmethod
    def remove_user_position(user):
        queue = SchedulerState.get_user_queue()
        userid = user['userid']
        for u in list(queue):
            if u['userid'] == userid:
                queue.remove(u)
                redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
                return True
        return False

    @staticmethod
    def set_is_alive(user):
        c_app = SchedulerState.get_current_app()
        if user['userid'] == c_app.get('userid', False):
            c_app['last_alive'] = time.time()
            SchedulerState.set_current_app(c_app)

    @staticmethod
    def get_user_queue():
        return json.loads(redis_get(SchedulerState.KEY_USERS_Q, '[]'))

    @staticmethod
    def start_user_app_request(username, userid, app_name, params, expires):
        queue = SchedulerState.get_user_queue()
        c_app = SchedulerState.get_current_app()
        removed_previous = True

        # New request from the same user sweeps older ones
        for i, job in enumerate(queue):
            if job['userid'] == userid:
                del queue[i]
                removed_previous = True

        # New request from the same user makes the current app expiring
        if c_app and c_app.get('userid', False) == userid:
            c_app['expire_at'] = str(datetime.datetime.now())
            SchedulerState.set_current_app(c_app)
            removed_previous = True

        app_struct = {'name': app_name,
                      'username': username,
                      'userid': userid,
                      'params': params,
                      'started_wait_at': datetime.datetime.now().isoformat(),
                      'expires': expires,
                      'task_id': None,
                      'last_alive': time.time(),
                      'expire_at': None}

        queue.append(app_struct)
        redis.set(SchedulerState.KEY_USERS_Q, json.dumps(queue))
        return True, removed_previous

    @staticmethod
    def check_db():
        if engine.dialect.has_table(engine.connect(), ConfigModel.__tablename__):
            session = session_factory()
            conf = session.query(ConfigModel).first()
            if conf is not None:
                return

        raise ValueError("Arbalet backend database has not been initialized. "
                         "Please run 'docker-compose run --rm app init' before starting the scheduler. "
                         "See INSTALL instructions for more information.")

    @staticmethod
    def restart_service():
        # Returns True if we could trigger a service restart, but can't guarantee it succeeded
        from os.path import isfile
        from os import system
        if isfile('/home/arbalet/Arbalet/frontage/docker-compose.prod.yml') and isfile('/usr/bin/docker-compose'):
            out = system('cd /home/arbalet/Arbalet/frontage && /usr/bin/docker-compose down')
            # Do not docker-compose up again, systemd will restart the stack
            if out == 0:
                return True
        return False
