#!/usr/bin/env python

from ._generator import gen_sweep_async
from .colors import Colors
from server.flaskutils import print_flush

class SweepAsync(Colors):

    def __init__(self, username, userid):
        Colors.__init__(self, gen_sweep_async, username, userid)
        self.PARAMS_LIST['uapp'] = ['swipe']
        print_flush("Init of SweepAsync", self.model.height, self.model.width)

    def run(self, params, expires_at=None):
        if not params:
            params = {}
        params['uapp'] = 'swipe'
        Colors.run(self, params, expires_at)
