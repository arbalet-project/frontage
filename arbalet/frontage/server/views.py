from __future__ import print_function

import json
import sys
import datetime

from server import app
from flask import request, jsonify, abort
from flask_restful import reqparse, abort, Api, Resource
from utils.security import authentication_required, generate_user_token
from utils.red import redis, redis_get
from scheduler import Scheduler
from scheduler_state import SchedulerState

def flask_log(msg):
    print(msg, file=sys.stderr)



api = Api(app)

@app.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True)

########### AUTH ###########

@app.route('/b/login', methods=['POST'])
def login():
    username = request.get_json().get('username', False)
    password = request.get_json().get('password', False)

    if ((username == 'frontageadmin') and password == 'frontagepassword'):
        return jsonify(login=True, token=generate_user_token(username))
    else:
        return jsonify(login=False)

########### ADMIN ###########

ADMIN_BASE = '/b/admin'

@app.route(ADMIN_BASE+'/is_on', methods=['GET'])
@authentication_required
def admin_is_on(user):
    return jsonify(on=SchedulerState.usable())

@app.route('/b/admin/cal', methods=['GET'])
@authentication_required
def admin_cal_at(user):
    return jsonify( on=SchedulerState.get_sundown().strftime('%H:%M'),
                    off=SchedulerState.get_sunrise().strftime('%H:%M'),
                    default="",
                    params={})



########### APP ###########

parser = reqparse.RequestParser()
parser.add_argument('type')
parser.add_argument('by')
parser.add_argument('comment')

class AppRuningView(Resource):
    @authentication_required
    def get(self, user):
        return jsonify( SchedulerState.get_current_app() )

    @authentication_required
    def delete(self, user):
        return '', 204

    @authentication_required
    def post(self, user):
        tags = []
        return tags


class AppListView(Resource):
    @authentication_required
    def get(self, user):
        return SchedulerState.get_available_apps()

########### PUBLIC ###########

@app.route('/frontage/status', methods=['GET'])
def status():
    state = SchedulerState.usable()
    return jsonify( is_usable=state,
                    scheduled_time=SchedulerState.default_scheduled_time(),
                    current_time=datetime.datetime.now())

@app.route('/frontage/next_date', methods=['GET'])
def next_date():
    state = SchedulerState.usable()
    return jsonify(is_usable=state)


api.add_resource(AppRuningView, '/b/admin/apps/running')
api.add_resource(AppListView, '/b/admin/apps')
