#!/usr/bin/env python
"""
    Arbalet Frontage

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import sys
import petname
import socket
from json import dumps, loads

from flask import Flask
from flask import request
from flask_cors import CORS
from flask import render_template
from flask import Response
from functools import wraps

from threading import RLock

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from time import time
from apps.fap import Fap
from utils.security import authentication_required, is_admin


class Snap(Fap):
    PLAYABLE = True
    ACTIVATED = False
    OFF = "Éteindre"

    def __init__(self, username=None):
        Fap.__init__(self, username)

        self.flask = Flask(__name__)
        self.current_auth_nick = self.OFF
        self.nicknames = {}
        self.lock = RLock()
        CORS(self.flask)
        self.port = int(33450)
        self.loop = None
        self.route()

    def route(self):

        #self.flask.route('/set_pixel_rgb', methods=['POST'])(self.set_pixel_rgb)
        self.flask.route('/set_rgb_matrix', methods=['POST'])(self.set_rgb_matrix)
        self.flask.route('/is_authorized/<nickname>', methods=['GET'])(self.is_authorized)
        self.flask.route('/get_nickname', methods=['GET'])(self.get_nickname)

        self.flask.route('/clients', methods=['GET'])(self.get_clients)
        self.flask.route('/authorize', methods=['POST'])(self.authorize)

    def check_nicknames_validity(self):
        with self.lock:
            temp_dict = {}
            for k, v in self.nicknames.items():
                if time() - v < 20:
                    temp_dict[k] = v
                else:
                    if k == self.current_auth_nick:
                        self.current_auth_nick = self.OFF
            self.nicknames = temp_dict

    @authentication_required
    def get_clients(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")

        return dumps({"list_clients": list(self.nicknames.keys()) + [self.OFF], "selected_client":self.current_auth_nick})

    @authentication_required
    def authorize(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")

        data = loads(request.get_data().decode())   # {selected_client: ""}
        if "selected_client" in data and data["selected_client"] in list(self.nicknames.keys()) + [self.OFF]:
            with self.lock:
                self.current_auth_nick = data["selected_client"]
                self.erase_all()
            return dumps({"success": True, "message": "Client authorized successfully"})
        abort(404, "No such client.")

    @staticmethod
    def scale(v):
        return min(1., max(0., float(v)/255))

    def set_rgb_matrix(self):
        try:
            data = request.get_data().decode().split(':')
            with self.lock:
                if data.pop(0) == self.current_auth_nick:
                    nb_rows = 4
                    nb_cols = 19
                    r = 0
                    c = 0
                    while data:
                        red = data.pop(0)
                        green = data.pop(0)
                        blue = data.pop(0)
                        self.model.set_pixel(r, c, list(map(self.scale, [red, green, blue])))
                        if c < nb_cols - 1:
                            c += 1
                        else:
                            c = 0
                            r += 1
        except Exception as e:
            raise e
            sys.exc_clear()
        else:
            self.send_model()
        return ''


    def erase_all(self):
        self.model.set_all("black")
        self.send_model()
        return ''

    def is_authorized(self, nickname):
        with self.lock:
            self.nicknames[nickname] = time()
        # update user table
        self.check_nicknames_validity()
        return str(nickname == self.current_auth_nick)

    def get_nickname(self):
        rand_id = petname.generate()
        with self.lock:
            while rand_id in self.nicknames.keys():
                rand_id = petname.generate()
            self.nicknames[rand_id] = time()
        return rand_id

    def run(self, params, expires_at=None):
        self.erase_all()
        self.loop = IOLoop()
        http_server = HTTPServer(WSGIContainer(self.flask))
        http_server.listen(self.port)
        self.loop.start()

