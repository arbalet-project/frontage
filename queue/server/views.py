import datetime
import json
import logging
from flask import request, jsonify, abort, Blueprint, g
from flask_restful import Resource
from utils.security import authentication_required, generate_user_token, is_admin, verify_password
from scheduler_state import SchedulerState
from server.extensions import rest_api
from flask_expects_json import expects_json
from utils.websock import Websock

# Version of protocol betwwen front and back. Mismatch = ask the user to update
PROTOCOL_VERSION = 3

blueprint = Blueprint('views', __name__)


@blueprint.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True, protocol_version=PROTOCOL_VERSION)


LOGIN_SCHEMA = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'}
    },
    'required': ['username']
}


@blueprint.route('/b/login', methods=['POST'])
@expects_json(LOGIN_SCHEMA)
def login():
    username = g.data.get('username', False)

    if username:
        return jsonify(
            login=True,
            token=generate_user_token(
                username=username,
                is_admin=False))
    else:
        return jsonify(login=False)


LOGIN_ADMIN_SCHEMA = {
    'type': 'object',
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'}
    },
    'required': ['username', 'password']
}


@blueprint.route('/b/adminlogin', methods=['POST'])
@expects_json(LOGIN_ADMIN_SCHEMA)
def login_admin():
    username = g.data.get('username', False)
    password = g.data.get('password', False)
    auth_username, hash = SchedulerState.get_admin_credentials()

    if (username == auth_username and verify_password(hash, password)):
        return jsonify(
            login=True,
            token=generate_user_token(
                username=username,
                is_admin=True))
    else:
        return jsonify(login=False)


ENABLE_SCHEMA = {
    'type': 'object',
    'properties': {
        'state': {'type': 'string'}
    },
    'required': ['state']
}


@blueprint.route('/b/admin/enabled', methods=['POST'])
@authentication_required
@expects_json(ENABLE_SCHEMA)
def admin_enabled_scheduler(user):
    state = g.data.get('state', 'on')
    if state not in ['on', 'off', 'scheduled']:
        abort(415, "Incorrect state")

    SchedulerState.set_enable_state(state)
    return jsonify(is_usable=SchedulerState.usable(),
                   is_forced=SchedulerState.get_forced_app(),
                   state=SchedulerState.get_enable_state(),
                   current_time=datetime.datetime.utcnow().isoformat())


@blueprint.route('/b/admin/cal', methods=['GET'])
def admin_cal_at():
    return jsonify(time_on=SchedulerState.get_time_on(),
                   time_off=SchedulerState.get_time_off(),
                   offset_time_on=SchedulerState.get_offset_time_on(),
                   offset_time_off=SchedulerState.get_offset_time_off())

# format .strftime('%Y-%m-%d')


@blueprint.route('/b/admin/state', methods=['PATCH'])
@authentication_required
def admin_set_state(user):
    if request.get_json().get('offset_time_on'):
        try:
            SchedulerState.set_offset_time_on(
                int(request.get_json().get('offset_time_on')))
        except ValueError:
            return jsonify(done=False)
    if request.get_json().get('offset_time_off'):
        try:
            SchedulerState.set_offset_time_off(
                int(request.get_json().get('offset_time_off')))
        except ValueError:
            return jsonify(done=False)
    if request.get_json().get('time_on'):
        SchedulerState.set_time_on(request.get_json()['time_on'])
    if request.get_json().get('time_off'):
        SchedulerState.set_time_off(request.get_json()['time_off'])
    return jsonify(done=True)


@blueprint.route('/b/admin/settings', methods=['POST'])
@authentication_required
def admin_set_settings(user):
    try:
        lifetime = int(request.get_json().get('default_lifetime'))
    except (ValueError, KeyError):
        return jsonify(done=False)
    else:
        SchedulerState.set_default_fap_lifetime(lifetime)
        return jsonify(done=True)


@blueprint.route('/b/admin/settings', methods=['GET'])
def admin_get_settings():
    return jsonify(default_lifetime=SchedulerState.get_default_fap_lifetime())


@blueprint.route('/b/apps/queue/clear', methods=['GET'])
@authentication_required
def admin_clear_queue(user):
    if is_admin(user):
        SchedulerState.stop_app_request(user)
        SchedulerState.clear_user_app_queue()
    else:
        abort(403, "Forbidden Bru")
    return '', 204


@blueprint.route('/b/apps/admin/running', methods=['POST'])
@authentication_required
def admin_app_force(user):
    req = request.get_json()
    if 'name' not in req:
        abort(415, 'Missing application name')

    name = req['name']
    params = req.get('params', {})

    forced = False
    if is_admin(user):
        if SchedulerState.set_forced_app_request(name, params):
            SchedulerState.clear_user_app_queue()
            SchedulerState.stop_app_request(user)
            forced = True
        return jsonify(keep_alive_delay=SchedulerState.DEFAULT_KEEP_ALIVE_DELAY,
                       forced=forced)
    else:
        abort(403, "Forbidden Bru")


@blueprint.route('/b/apps/admin/quit', methods=['GET'])
@authentication_required
def admin_app_quit(user):
    if is_admin(user):
        if (SchedulerState.get_current_app()['name'] == "Snap"):
            Websock.set_grantUser({'id': "turnoff", 'username': "turnoff"})
        removed = SchedulerState.stop_forced_app_request(user)
        return jsonify(removed=removed)
    else:
        abort(403, "Forbidden Bru")
    return '', 204


class AppRunningView(Resource):
    @authentication_required
    def get(self, user):
        while SchedulerState.is_event_lock():
            pass
        return jsonify(SchedulerState.get_current_app())

    @authentication_required
    def post(self, user):
        name = request.get_json()['name']
        params = request.get_json().get('params', {})
        expires = SchedulerState.get_expires_value()

        queued, removed_previous = SchedulerState.start_user_app_request(
            user['username'], user['userid'], name, params, expires)
        return jsonify(queued=queued, removed_previous=removed_previous,
                       keep_alive_delay=SchedulerState.DEFAULT_KEEP_ALIVE_DELAY)


class ConfigView(Resource):
    @authentication_required
    def get(self, user):
        return SchedulerState.get_expires_value()

    def post(self, user):
        expire = request.get_json()['value']
        return SchedulerState.set_expires_value(expire)


class AppDefaultListView(Resource):
    @authentication_required
    def get(self, user):
        return True

    def post(self, user):
        return True


class DrawingAppDefault(Resource):
    @authentication_required
    def post(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")
        return jsonify(done=SchedulerState.set_default_drawing())


class AppDefaultParamView(Resource):
    @authentication_required
    def get(self, user, app_name):
        return SchedulerState.get_default_scheduled_app_params(app_name, serialized=True)

    @authentication_required
    def post(self, user, app_name):
        if not is_admin(user):
            abort(403, "Forbidden Bru")
        params = request.get_json().get('params', None)

        return jsonify(done=SchedulerState.set_default_scheduled_app_params(app_name, params))


class AppDefaultView(Resource):
    @authentication_required
    def get(self, user):
        return SchedulerState.get_default_scheduled_apps(serialized=True)

    @authentication_required
    def post(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")

        app_state_bool = request.get_json().get('app_state', False)
        SchedulerState.set_default_scheduled_app_state(
            request.get_json().get('app_name'), app_state_bool)

        return SchedulerState.get_default_scheduled_apps(serialized=True)


class AppListView(Resource):
    @authentication_required
    def get(self, user):
        apps = SchedulerState.get_available_apps()
        if is_admin(user):
            apps = SchedulerState.get_available_apps()
        else:
            apps = {k: v for k, v in apps.items() if v['activated']}

        formated = []
        defaults_apps = SchedulerState.get_default_scheduled_apps(
            serialized=False)
        defaults_apps_names = [x['name'] for x in defaults_apps]
        for x in apps:
            ext_app = apps[x]
            ext_app['scheduled'] = False if (
                x not in defaults_apps_names) else True
            formated.append(ext_app)
        return formated


@blueprint.route('/b/apps/position', methods=['GET'])
@authentication_required
def app_position(user):
    return jsonify(position=SchedulerState.get_user_position(user))


@blueprint.route('/b/apps/iamalive', methods=['POST'])
@authentication_required
def set_is_alive_current_app(user):
    SchedulerState.set_is_alive(user)
    c_app = SchedulerState.get_current_app()
    keep_alive = "userid" in c_app and c_app['userid'] == user['userid']
    return jsonify(keepAlive=keep_alive)


@blueprint.route('/b/apps/quit', methods=['GET'])
@authentication_required
def quit_user_app(user):
    c_app = SchedulerState.get_current_app()
    removed = False
    if is_admin(user) or c_app.get('userid', False) == user['userid']:
        SchedulerState.stop_app_request(user)
        removed = True
    return jsonify(removed=removed)


@blueprint.route('/b/queue/quit', methods=['GET'])
@authentication_required
def remove_from_queue(user):
    if SchedulerState.remove_user_position(user):
        return jsonify(removed=True)
    else:
        return jsonify(removed=False)


@blueprint.route('/frontage/status', methods=['GET'])
def status():
    c_app = SchedulerState.get_current_app()
    c_app_name = c_app.get('name', '') if c_app else ''
    return jsonify(is_usable=SchedulerState.usable(),
                   is_forced=SchedulerState.get_forced_app(),
                   current_app=c_app_name,
                   next_on_time=SchedulerState.get_scheduled_on_time().isoformat(),
                   state=SchedulerState.get_enable_state(),
                   current_time=datetime.datetime.utcnow().isoformat(),
                   height=SchedulerState.get_rows(),
                   width=SchedulerState.get_cols(),
                   disabled=SchedulerState.get_disabled(),
                   version=SchedulerState.get_version())


@blueprint.route('/b/restart', methods=['POST'])
@authentication_required
def restart_service(user):
    if is_admin(user):
        return jsonify(done=SchedulerState.restart_service())
    return jsonify(done=False)


rest_api.add_resource(ConfigView, '/b/config/')

rest_api.add_resource(AppDefaultView, '/b/apps/default/')
rest_api.add_resource(AppDefaultParamView, '/b/apps/default/<string:app_name>')
rest_api.add_resource(AppDefaultListView, '/b/apps/default')
rest_api.add_resource(DrawingAppDefault, '/b/apps/drawing/default')

rest_api.add_resource(AppRunningView, '/b/apps/running')
rest_api.add_resource(AppListView, '/b/apps')

# ARBALET LIVE


@blueprint.route('/b/admin/snap/users', methods=['GET'])
@authentication_required
def get_users(user):
    if (not is_admin(user)):
        abort(403, "Forbidden Bru")
    users = (json.loads(Websock.get_users()))['users']
    guser = (json.loads(Websock.get_grantUser()))
    return jsonify(list_clients=users, selected_client=guser)


@blueprint.route('/b/admin/snap/guser', methods=['POST'])
@authentication_required
def set_user(user):
    if (not is_admin(user)):
        abort(403, "Forbidden Bru")
    body = request.get_json()
    id = body['selected_client']
    users = (json.loads(Websock.get_users()))['users']
    guser = None
    if (id != "turnoff"):
        for user in users:
            if (user['id'] == id):
                guser = user
        if (guser == None):
            return jsonify(success=False, message="No such client")
    else:
        guser = {'id': "turnoff", 'username': "turnoff"}
    Websock.set_grantUser(guser)
    return jsonify(success=True, message="Client authorized successfully")


CONFIG_DIM_SCHEMA = {
    'type': 'object',
    'properties': {
        'columns': {'type': 'number'},
        'rows': {'type': 'number'},
    },
    'required': ['columns', 'rows']
}


@blueprint.route('/b/admin/config/dimensions', methods=['POST'])
@authentication_required
@expects_json(CONFIG_DIM_SCHEMA)
def load_dimensions_config(user):
    # Configure width and height.
    if is_admin(user):
        SchedulerState.set_cols(g.data.get('columns', 0))
        SchedulerState.set_rows(g.data.get('rows', 0))
        return jsonify(success=True)
    else:
        return jsonify(success=False)


CONFIG_GENERAL_SCHEMA = {
    'type': 'object',
    'properties': {
        'id': {'type': 'string'},
        'name': {'type': 'string'},
    },
    'required': ['id', 'name']
}


@blueprint.route('/b/admin/config/general', methods=['POST'])
@authentication_required
@expects_json(CONFIG_GENERAL_SCHEMA)
def load_general_config(user):
    # Configure id and name of the apps.
    if is_admin(user):
        SchedulerState.set_id(g.data.get('id', ''))
        SchedulerState.set_name(g.data.get('name', ''))
        return jsonify(success=True)
    else:
        return jsonify(success=False)


CONFIG_MAPPINGS_SCHEMA = {
    'type': 'object',
    'properties': {
        'mappings': {'type': 'array'},
    },
    'required': ['mappings']
}


@blueprint.route('/b/admin/config/mappings', methods=['POST'])
@authentication_required
@expects_json(CONFIG_MAPPINGS_SCHEMA)
def load_mapping_config(user):
    # Configure id and name of the apps.
    if is_admin(user):
        mappings = g.data.get('mappings', [])
        print(len(mappings), flush=True)
        print(len(mappings[0]), flush=True)
        for row in range(len(mappings)):
            for col in range(len(mappings[row])):
                SchedulerState.set_mappings(row, col, mappings[row][col])
        return jsonify(success=True)
    else:
        return jsonify(success=False)
