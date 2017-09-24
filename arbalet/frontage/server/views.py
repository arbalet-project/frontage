from __future__ import print_function

import json
import sys
import datetime

from server import app
from flask import request, jsonify, abort
from flask_restful import reqparse, abort, Api, Resource
from utils.security import authentication_required
from utils.red import redis, redis_get
from scheduler import Scheduler
from tasks.tasks import start_scheduler

def flask_log(msg):
    print(msg, file=sys.stderr)



api = Api(app)

@app.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True)

@app.route('/b/start', methods=['GET'])
def scheduler_start():
    start_scheduler.delay()
    return jsonify(started=True)
########### AUTH ###########

@app.route('/b/login', methods=['POST'])
@authentication_required
def login():
    return jsonify(is_up=True)

########### ADMIN ###########

ADMIN_BASE = '/b/admin'

@app.route(ADMIN_BASE+'/is_on', methods=['GET'])
@authentication_required
def admin_is_on():
    return jsonify(is_on=True)

@app.route('/b/admin/cal/<timestamp>', methods=['GET'])
@authentication_required
def admin_cal_at(timestamp):
    return jsonify( on=Scheduler.get_sundown().strftime('%H:%M'),
                    off=Scheduler.get_sunrise().strftime('%H:%M'),
                    default="",
                    params={})

########### APP ###########

parser = reqparse.RequestParser()
parser.add_argument('type')
parser.add_argument('by')
parser.add_argument('comment')

class AppRuningView(Resource):
    @authentication_required
    def get(self):
        return []

    @authentication_required
    def delete(self):
        return '', 204

    @authentication_required
    def get(self):
        tags = []
        return tags


class AppListView(Resource):
    @authentication_required
    def get(self):
        return Scheduler.get_available_apps()

########### PUBLIC ###########

@app.route('/frontage/status', methods=['GET'])
def status():
    state = Scheduler.usable()
    return jsonify( is_usable=state,
                    scheduled_time=Scheduler.default_scheduled_time(),
                    current_time=datetime.datetime.now())

@app.route('/frontage/next_date', methods=['GET'])
def next_date():
    state = Scheduler.usable()
    return jsonify(is_usable=state)


# api.add_resource(AppRuningView, '/api/views')
api.add_resource(AppListView, '/b/admin/apps')
