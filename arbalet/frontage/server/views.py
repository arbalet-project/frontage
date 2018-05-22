import datetime

from flask import request, jsonify, abort, Blueprint, g
from flask_restful import Resource
from utils.security import authentication_required, generate_user_token, is_admin, verify_password
from scheduler_state import SchedulerState
from server.extensions import rest_api
from server.flaskutils import print_flush
from flask_expects_json import expects_json

PROTOCOL_VERSION = 1   # Version of protocol betwwen front and back. Mismatch = ask the user to update

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
        abort(415)
    SchedulerState.set_enable_state(state)
    return jsonify(is_usable=SchedulerState.usable(),
                   state=SchedulerState.get_enable_state(),
                   current_time=datetime.datetime.now().isoformat())


@blueprint.route('/b/admin/cal', methods=['GET'])
def admin_cal_at():
    return jsonify(on=SchedulerState.get_forced_on_time(),
                   off=SchedulerState.get_forced_off_time(),
                   on_offset=SchedulerState.get_sundown_offset(),
                   off_offset=SchedulerState.get_sunrise_offset())

# format .strftime('%Y-%m-%d')


@blueprint.route('/b/admin/state', methods=['PATCH'])
@authentication_required
def admin_set_state(user):
    if request.get_json().get('sunrise_offset'):
        SchedulerState.set_sunrise_offset(request.get_json().get('sunrise_offset', 0))
    if request.get_json().get('sundown_offset'):
        SchedulerState.set_sunset_offset(request.get_json().get('sundown_offset', 0))
    if request.get_json().get('sunrise'):
        SchedulerState.set_forced_off_time(request.get_json()['sunrise'])
    if request.get_json().get('sundown'):
        SchedulerState.set_forced_on_time(request.get_json()['sundown'])

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
        SchedulerState.clear_user_app_queue()
    else:
        abort(400, "Forbidden Bru")
    return '', 204


class AppAdminRunningView(Resource):
    @authentication_required
    def post(self, user):
        req = request.get_json()
        if 'name' not in req:
            abort(400, 'Missing application name')

        name = req['name']
        params = req.get('params', {})

        if not SchedulerState.usable():
            print_flush("Frontage is not started")
            abort(400, "Frontage is not started")
        if is_admin(user):
            response = SchedulerState.set_forced_app_request(name, params)
            if response:
                return response
            else:
                abort(409, 'An app is already forced')
        else:
            abort(403, "Forbidden Bru")

    @blueprint.route('/b/apps/admin/quit', methods=['GET'])
    @authentication_required
    def admin_app_quit(self, user):
        if is_admin(user):
            if not SchedulerState.stop_forced_app_request():
                abort(404, "No such app")
        else:
            abort(400, "Forbidden Bru")
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
        if not SchedulerState.usable():
            print_flush("Frontage is not started")
            abort(400, "Frontage is not started")

        try:
            return SchedulerState.start_user_app_request(user['username'], name, params, expires)
        except Exception as e:
            print_flush(str(e))
            abort(403, str(e))
        # SchedulerState.set_forced_app(name, params, expires)


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
        SchedulerState.set_default_scheduled_app_state(request.get_json().get('app_name'), app_state_bool)

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
        defaults_apps = SchedulerState.get_default_scheduled_apps(serialized=False)
        defaults_apps_names = [x['name'] for x in defaults_apps]
        for x in apps:
            ext_app = apps[x]
            ext_app['scheduled'] = False if (x not in defaults_apps_names) else True
            formated.append(ext_app)
        return formated


@blueprint.route('/b/apps/position', methods=['GET'])
@authentication_required
def app_position(user):
    return jsonify(position=SchedulerState.get_user_position(user))

@blueprint.route('/b/apps/iamalive', methods=['POST'])
@authentication_required
def set_is_alive_current_app(user):
    SchedulerState.set_is_alive_current_app(user['username'])
    return jsonify(pouet='pouet')

@blueprint.route('/b/apps/quit', methods=['GET'])
@authentication_required
def quit_user_app(user):
    c_app = SchedulerState.get_current_app()
    if 'username' in c_app:
        if is_admin(user):
            SchedulerState.stop_app_request()
        else:
            if c_app['username'] == user['username']:
                SchedulerState.stop_app_request()
            else:
                abort(400, "You are not the owner of the current app")
    else:
        print("Tried to quit an app while no one was running, ignoring request.")
        abort(400, "No app found. Nothing to quit.")
    return '', 204

@blueprint.route('/b/queue/quit', methods=['GET'])
@authentication_required
def remove_from_queue(user):
    if SchedulerState.remove_user_position(user):
        return jsonify(removed=True)
    else:
        abort(404, "I can't find any app for you")
    return jsonify(removed=False)


@blueprint.route('/frontage/status', methods=['GET'])
def status():
    return jsonify(is_usable=SchedulerState.usable(),
                   next_on_time=SchedulerState.get_scheduled_on_time().isoformat(),
                   state=SchedulerState.get_enable_state(),
                   current_time=datetime.datetime.now().isoformat())


rest_api.add_resource(ConfigView, '/b/config/')

rest_api.add_resource(AppDefaultView, '/b/apps/default/')
rest_api.add_resource(AppDefaultParamView, '/b/apps/default/<string:app_name>')
rest_api.add_resource(AppDefaultListView, '/b/apps/default')

rest_api.add_resource(AppAdminRunningView, '/b/apps/admin/running')
rest_api.add_resource(AppRunningView, '/b/apps/running')
rest_api.add_resource(AppListView, '/b/apps')
