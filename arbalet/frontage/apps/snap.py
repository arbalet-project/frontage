#!/usr/bin/env python
"""
    Arbalet Frontage

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import sys
import petname
from json import dumps, loads

from flask import Flask, request, abort
from flask_cors import CORS

from threading import RLock

# from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from time import time
from apps.fap import Fap
from scheduler_state import SchedulerState
from utils.security import authentication_required, is_admin


class Snap(Fap):
    PLAYABLE = True
    ACTIVATED = False
    OFF = "turnoff"

    def __init__(self, username, userid):
        Fap.__init__(self, username, userid)

        self.flask = Flask(__name__)
        self.current_auth_nick = self.OFF
        self.nicknames = {}
        self.lock = RLock()
        CORS(self.flask)
        self.port = int(50000)
        self.loop = None
        self.route()

    def route(self):
        ## Routes pour le client snap
        #self.flask.route('/set_pixel_rgb', methods=['POST'])(self.set_pixel_rgb)
        self.flask.route('/set_rgb_matrix', methods=['POST'])(self.set_rgb_matrix)
        self.flask.route('/is_authorized/<nickname>', methods=['GET'])(self.is_authorized)
        self.flask.route('/get_nickname', methods=['GET'])(self.get_nickname)

        ## Routes pour l'application mobile
        self.flask.route('/clients', methods=['GET'])(self.get_clients)
        self.flask.route('/authorize', methods=['POST'])(self.authorize)

    def check_nicknames_validity(self):
        with self.lock:
            temp_dict = {}
            for nick, timestamps in self.nicknames.items():
                if time() - timestamps["last_seen"] < 20:
                    temp_dict[nick] = timestamps
                else:
                    if nick == self.current_auth_nick:
                        self.current_auth_nick = self.OFF
            self.nicknames = temp_dict

    #request handler for mobile application (send the client list)
    @authentication_required
    def get_clients(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")
        # update user table
        self.check_nicknames_validity()
        return dumps({"list_clients": sorted(self.nicknames.keys(), key=lambda x: self.nicknames[x]["appeared"]), "selected_client":self.current_auth_nick})

    #request handler for mobile application (put a client on realtime display)
    @authentication_required
    def authorize(self, user):
        if not is_admin(user):
            abort(403, "Forbidden Bru")

        data = loads(request.get_data().decode())   # {selected_client: ""}
        with self.lock:
            if "selected_client" in data and data["selected_client"] in [self.OFF] + list(self.nicknames.keys()):
                self.current_auth_nick = data["selected_client"]
                self.erase_all()
                return dumps({"success": True, "message": "Client authorized successfully"})
        return dumps({"success": False, "message": "No such client"})

    @staticmethod
    def scale(v):
        return min(1., max(0., float(v)/255))

    def set_rgb_matrix(self):
        data = request.get_data().decode().split(':')
        if data.pop(0) == self.current_auth_nick:
            nb_rows = SchedulerState.get_rows()
            nb_cols = SchedulerState.get_cols()
            r = 0
            c = 0
            with self.lock:
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
                self.send_model()
                return 'OK'
        abort(403, "Snap client not authorized")

    def erase_all(self):
        with self.lock:
            self.model.set_all("black")
            self.send_model()
        return 'OK'

    def is_authorized(self, nickname):
        with self.lock:
            self.nicknames[nickname]["last_seen"] = time()
        return str(nickname == self.current_auth_nick)

    def get_nickname(self):
        rand_id = petname.generate()
        with self.lock:
            while rand_id in self.nicknames.keys():
                rand_id = petname.generate()
            self.nicknames[rand_id] = {"appeared": time(), "last_seen": time()}
        return rand_id

    def run(self, params, expires_at=None):
        self.start_socket()
        from tornado.wsgi import WSGIContainer

        self.erase_all()
        self.loop = IOLoop()
        http_server = HTTPServer(WSGIContainer(self.flask))
        http_server.listen(self.port)
        self.loop.start()
