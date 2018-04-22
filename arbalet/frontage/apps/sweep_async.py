#!/usr/bin/env python

from ._generator import gen_sweep_async
from .colors import Colors


class SweepAsync(Colors):

    def __init__(self, username=None):
        Colors.__init__(self, gen_sweep_async, username)
        self.PARAMS_LIST['uapp'] = ['swipe']

    def run(self, params, expires_at=None):
        if not params:
            params = {}
        params['uapp'] = 'swipe'
        Colors.run(self, params, expires_at)
