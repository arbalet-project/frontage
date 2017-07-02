#!/usr/bin/env python
"""
    Arbalet Frontage

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""

from flask import Flask
from flask_cors import CORS


class SnapServer(object):
    def __init__(self, port):
        super(SnapServer, self).__init__()
        self.flask = Flask(__name__)
        CORS(self.flask)
        self.port = int(port)
        self.route()

    def route(self):
        self.flask.route('/set_pixel/<h>/<w>/<color>', methods=['GET'])(self.set_pixel)
        self.flask.route('/set_pixel_rgb/<h>/<w>/<r>/<g>/<b>', methods=['GET'])(self.set_pixel_rgb)
        self.flask.route('/erase_all', methods=['GET'])(self.erase_all)

    def set_pixel(self, h, w, color):
        self.model.set_pixel(int(h) - 1, int(w) - 1, color)
        return ''

    def erase_all(self):
        self.model.set_all('black')
        return ''

    def set_pixel_rgb(self, h, w, r, g, b):
        def scale(v):
            return min(1., max(0., float(v)/255.))
        self.model.set_pixel(int(h) - 1, int(w) - 1, map(scale, [r, g, b]))
        return ''

    def run(self):
        self.flask.run(host='0.0.0.0', port=self.port)
