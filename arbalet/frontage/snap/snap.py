#!/usr/bin/env python
"""
    Arbalet Frontage

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from flask import Flask
from flask_cors import CORS
from ..hardware import Frontage


class SnapServer(object):
    def __init__(self, port):
        super(SnapServer, self).__init__()
        self.flask = Flask(__name__)
        self.frontage = Frontage(33460)  # Blocking until the hardware client connects

        CORS(self.flask)
        self.port = int(port)
        self.route()

    def route(self):
        self.flask.route('/set_pixel_rgb/<h>/<w>/<r>/<g>/<b>', methods=['GET'])(self.set_pixel_rgb)
        self.flask.route('/erase_all', methods=['GET'])(self.erase_all)

    def erase_all(self):
        self.frontage.set_all(0, 0, 0)
        return ''

    def set_pixel_rgb(self, h, w, r, g, b):
        def scale(v):
            return min(255, max(0, int(v)))
        self.frontage[int(h) - 1, int(w) - 1] = map(scale, (r, g, b))
        return ''

    def run(self):
        self.flask.run(host='0.0.0.0', port=self.port)
