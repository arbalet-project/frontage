from __future__ import print_function

import json
import sys

from server import app
from flask import request, jsonify, abort
from flask_restful import reqparse, abort, Api, Resource

def flask_log(msg):
    print(msg, file=sys.stderr)

@app.route('/status/is_up', methods=['GET'])
def is_up():
    return jsonify(is_up=True)

########### AUTH ###########

@app.route('/b/login', methods=['POST'])
def login():
    return jsonify(is_up=True)

########### ADMIN ###########

ADMIN_BASE = '/b/admin'

@app.route(ADMIN_BASE+'/is_on', methods=['GET'])
def admin_is_on():
    return jsonify(is_up=True)

@app.route('/b/admin/cal/<timestamp>', methods=['GET'])
def admin_cal_at():
    return jsonify(is_up=True)

########### APP ###########

parser = reqparse.RequestParser()
parser.add_argument('type')
parser.add_argument('by')
parser.add_argument('comment')

class AppRuningView(Resource):
    def get(self):
        return []

    def delete(self):
        return '', 204

    def get(self):
        tags = []
        for s in Tag.query.all():
            d = serialize(to_dict(s))
            tags.append(d)
        return tags


class AppListView(Resource):
    def get(self):
        tags = []
        return tags


api.add_resource(AppListView, ADMIN_BASE+'/apps')
api.add_resource(AppRuningView, ADMIN_BASE+'/apps/running')