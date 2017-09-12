from __future__ import print_function

import json
import sys

from server import app
from flask import request, jsonify, abort
from flask_restful import reqparse, abort, Api, Resource
from utils.security import authentication_required
from utils.red import redis, redis_get
from scheduler import Scheduler

def flask_log(msg):
    print(msg, file=sys.stderr)


api = Api(app)

@app.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True)

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
    return jsonify(is_up=True)

@app.route('/b/admin/cal/<timestamp>', methods=['GET'])
@authentication_required
def admin_cal_at():
    return jsonify(is_up=True)

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
        tags = []
        return tags

########### PUBLIC ###########

@app.route('/frontage/status', methods=['GET'])
def status():
    state = True if (redis_get(Scheduler.KEY_USABLE, False) == 'True') else False
    return jsonify(is_usable=state)