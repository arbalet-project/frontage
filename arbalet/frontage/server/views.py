from __future__ import print_function

import sys
import datetime

from flask import request, jsonify, abort, Blueprint
from flask_restful import reqparse, Resource
from utils.security import authentication_required, generate_user_token, is_admin
from scheduler_state import SchedulerState
from server.extensions import rest_api


def flask_log(msg):
    print(msg, file=sys.stderr)


blueprint = Blueprint('views', __name__)


@blueprint.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True)


@blueprint.route('/b/login', methods=['POST'])
def login():
    username = request.get_json().get('username', False)
    password = request.get_json().get('password', False)

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


ADMIN_BASE = '/b/admin'


@blueprint.route(ADMIN_BASE + '/enabled', methods=['POST'])
@authentication_required
def admin_enabled_scheduler(user):
    SchedulerState.set_usable(request.get_json().get('enabled', False))
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


parser = reqparse.RequestParser()
parser.add_argument('type')
parser.add_argument('by')
parser.add_argument('comment')


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
        expires = request.get_json().get('expires', 20)
        if not SchedulerState.usable():
            flask_log("Frontage is not started")
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
        if is_admin(user):
            SchedulerState.stop_app(c_app)
        else:
            if c_app['username'] == user['username']:
                SchedulerState.stop_app(c_app)
            else:
                abort(400, "You are not the owner of the current app")

        return '', 204

    @authentication_required
    def post(self, user):
        name = request.get_json()['name']
        params = request.get_json()['params']
        expires = request.get_json().get('expires', 20)
        if not SchedulerState.usable():
            flask_log("Frontage is not started")
            abort(400, "Frontage is not started")

        try:
            return SchedulerState.start_scheduled_app(
                user['username'], name, params, expires)
        except Exception as e:
            flask_log(str(e))
            abort(403, str(e))
        # SchedulerState.set_forced_app(name, params, expires)


class AppDefaultListView(Resource):
    @authentication_required
    def get(self, user):
        return True

    def post(self, user):
        return True


class AppDefaultView(Resource):
    @authentication_required
    def get(self, user):
        return True
    #     return SchedulerState.get_default_scheduled_app(serialized=True)

    # def delete(self, user):
    #     SchedulerState.set_default_scheduled_app_state(request.get_json().get('app_name'), False)

    #     return SchedulerState.get_default_scheduled_app(serialized=True)

    # def post(self, user):
    #     SchedulerState.set_default_scheduled_app_state(request.get_json().get('app_name'), True)

    #     return SchedulerState.get_default_scheduled_app(serialized=True)


class AppListView(Resource):
    @authentication_required
    def get(self, user):
        apps = SchedulerState.get_available_apps()
        if is_admin(user):
            apps = SchedulerState.get_available_apps()
        else:
            apps = {k: v for k, v in apps.items() if v['activated']}

        formated = []
        for x in apps:
            formated.append(apps[x])
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
                   scheduled_time=SchedulerState.default_scheduled_time(),
                   current_time=datetime.datetime.now().isoformat())


@blueprint.route('/frontage/next_date', methods=['GET'])
def next_date():
    state = SchedulerState.usable()
    return jsonify(is_usable=state)


rest_api.add_resource(AppDefaultView, '/b/apps/default/')
rest_api.add_resource(AppDefaultListView, '/b/apps/default')

rest_api.add_resource(AppAdminRuningView, '/b/apps/admin/running')
rest_api.add_resource(AppRuningView, '/b/apps/running')
rest_api.add_resource(AppQueueView, '/b/apps/queue')
rest_api.add_resource(AppListView, '/b/apps')
