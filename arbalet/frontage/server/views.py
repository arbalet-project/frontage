import datetime

from flask import request, jsonify, abort, Blueprint, g
from flask_restful import Resource
from utils.security import authentication_required, generate_user_token, is_admin
from scheduler_state import SchedulerState
from server.extensions import rest_api
from server.flaskutils import print_flush
from flask_expects_json import expects_json


blueprint = Blueprint('views', __name__)


@blueprint.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True)


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
    password = g.data.get('password', False)

    if ((username == 'frontageadmin') and password == 'frontagepassword'):
        return jsonify(
            login=True,
            token=generate_user_token(
                username=username,
                is_admin=True))
    elif username:
        return jsonify(
            login=True,
            token=generate_user_token(
                username=username,
                is_admin=False))
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
    return jsonify(enabled=SchedulerState.usable())


@blueprint.route('/b/admin/cal', methods=['GET'])
@blueprint.route('/b/admin/cal/<at>', methods=['GET'])
def admin_cal_at(at=None):
    return jsonify(on=SchedulerState.get_sundown(at).strftime('%H:%M'),
                   off=SchedulerState.get_sunrise(at).strftime('%H:%M'),
                   default="",
                   params={})

# format .strftime('%Y-%m-%d')


@blueprint.route('/b/admin/cal/<at>', methods=['PATCH'])
@authentication_required
def admin_set_cal_at(user, at):
    if request.get_json().get('on'):
        SchedulerState.set_sundown(day=at, at=request.get_json()['on'])
    if request.get_json().get('off'):
        SchedulerState.set_sunrise(day=at, at=request.get_json()['off'])

    return jsonify(on=SchedulerState.get_sundown(at).strftime('%H:%M'),
                   off=SchedulerState.get_sunrise(at).strftime('%H:%M'),
                   default="",
                   params={})


@blueprint.route('/b/admin/state', methods=['PATCH'])
@authentication_required
def admin_set_state(user):
    if request.get_json().get('sunrise_offset'):
        SchedulerState.set_sunrise_offset(request.get_json().get('sunrise_offset', 0))
    if request.get_json().get('sundown_offset'):
        SchedulerState.set_sundown_offset(request.get_json().get('sundown_offset', 0))
    if request.get_json().get('sunrise'):
        SchedulerState.set_forced_sunrise(request.get_json()['sunrise'])
    if request.get_json().get('sundown'):
        SchedulerState.set_forced_sundown(request.get_json()['sundown'])

    return jsonify(done=True)


class AppQueueView(Resource):
    @authentication_required
    def delete(self, user):
        if is_admin(user):
            SchedulerState.clear_user_app_queue()
        else:
            abort(400, "Forbidden Bru")

        return '', 204


class AppAdminRuningView(Resource):
    @authentication_required
    def post(self, user):
        name = request.get_json()['name']
        params = request.get_json()['params']
        expires = request.get_json().get('expires', SchedulerState.get_expires_value())

        if not SchedulerState.usable():
            print_flush("Frontage is not started")
            abort(400, "Frontage is not started")
        if is_admin(user):
            SchedulerState.set_forced_app(name, params, expires)
            return True
        else:
            abort(403, "Forbidden Bru")


class AppRuningView(Resource):
    @authentication_required
    def get(self, user):
        return jsonify(SchedulerState.get_current_app())

    @authentication_required
    def delete(self, user):
        c_app = SchedulerState.get_current_app()
        if 'username' in c_app:
            if is_admin(user):
                SchedulerState.stop_app(c_app)
            else:
                if c_app['username'] == user['username']:
                    SchedulerState.stop_app(c_app)
                else:
                    abort(400, "You are not the owner of the current app")
        else:
            print("Tried to delete an app while no one was running, ignoring delete request.")
        return '', 204

    @authentication_required
    def post(self, user):
        name = request.get_json()['name']
        params = request.get_json().get('params', {})
        expires = request.get_json().get('expires', 20)
        if not SchedulerState.usable():
            print_flush("Frontage is not started")
            abort(400, "Frontage is not started")

        try:
            return SchedulerState.start_scheduled_app(
                user['username'], name, params, expires)
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

        return SchedulerState.set_default_scheduled_app_params(app_name, params)


class AppDefaultView(Resource):
    @authentication_required
    def get(self, user):
        return SchedulerState.get_default_scheduled_app(serialized=True)

    def delete(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")
        SchedulerState.set_default_scheduled_app_state(request.get_json().get('app_name'), False)

        return SchedulerState.get_default_scheduled_app(serialized=True)

    @authentication_required
    def post(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")

        app_state_bool = request.get_json().get('app_state', False)
        SchedulerState.set_default_scheduled_app_state(request.get_json().get('app_name'), app_state_bool)

        return SchedulerState.get_default_scheduled_app(serialized=True)


class AppListView(Resource):
    @authentication_required
    def get(self, user):
        apps = SchedulerState.get_available_apps()
        if is_admin(user):
            apps = SchedulerState.get_available_apps()
        else:
            apps = {k: v for k, v in apps.items() if v['activated']}

        formated = []
        defaults_apps = SchedulerState.get_default_scheduled_app(serialized=False)
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


@blueprint.route('/b/apps/position', methods=['DELETE'])
@authentication_required
def remove_from_queue(user):
    if SchedulerState.remove_user_position(user):
        return jsonify(removed=True)
    else:
        abort(404, "I can't find any app for you")
    return jsonify(removed=False)


@blueprint.route('/frontage/status', methods=['GET'])
def status():
    state = SchedulerState.usable()
    return jsonify(is_usable=state,
                   state=SchedulerState.get_enable_state(),
                   scheduled_time=SchedulerState.default_scheduled_time(),
                   current_time=datetime.datetime.now().isoformat())


@blueprint.route('/frontage/status', methods=['POST'])
def status_post():
    # CAHNGE VALUE
    return jsonify(is_usable=SchedulerState.usable())


@blueprint.route('/frontage/next_date', methods=['GET'])
def next_date():
    state = SchedulerState.usable()
    return jsonify(is_usable=state)


rest_api.add_resource(ConfigView, '/b/config/')

rest_api.add_resource(AppDefaultView, '/b/apps/default/')
rest_api.add_resource(AppDefaultParamView, '/b/apps/default/<string:app_name>')
rest_api.add_resource(AppDefaultListView, '/b/apps/default')

rest_api.add_resource(AppAdminRuningView, '/b/apps/admin/running')
rest_api.add_resource(AppRuningView, '/b/apps/running')
rest_api.add_resource(AppQueueView, '/b/apps/queue')
rest_api.add_resource(AppListView, '/b/apps')
