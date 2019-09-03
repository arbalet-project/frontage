#!/usr/bin/env python


from ._generator import gen_sweep_rand
from .colors import Colors
from json import loads

class SweepRand(Colors):

    def __init__(self, username, userid):
        Colors.__init__(self, gen_sweep_rand, username, userid)
        self.PARAMS_LIST['uapp'] = ['road', 'gender', 'cold', 'warm']

    def handle_message(self, data, path=None): # noqa
        if not self.LOCK_WS.acquire_write(2):
            return
        if data is not None:
            params = loads(data)
            if params['uapp'] in self.PARAMS_LIST['uapp']:
                self.process_params(params)
                self.create_generator()
        self.LOCK_WS.release()
