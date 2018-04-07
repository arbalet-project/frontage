#!/usr/bin/env python

from ._generator import gen_sweep_async
from .colors import Colors


class SweepAsync(Colors):

    def __init__(self):
        Colors.__init__(self, gen_sweep_async)
        self.PARAMS_LIST['uapp'] = ['swipe']

    def run(self, params, expires_at=None):
        params['colors'] = 'blueviolet'
        Colors.run(params, expires_at)
