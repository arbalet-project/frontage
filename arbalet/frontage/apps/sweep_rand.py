#!/usr/bin/env python


from ._generator import gen_sweep_rand
from .colors import Colors
from json import loads
from server.flaskutils import print_flush


class SweepRand(Colors):

    def __init__(self, username, userid):
        Colors.__init__(self, gen_sweep_rand, username, userid)
        self.PARAMS_LIST['uapp'] = ['road', 'gender', 'cold', 'warm']
        print_flush("Init of SweepRand", self.model.height, self.model.width)

    def handle_message(self, data, path=None): # noqa
        if not self.LOCK_WS.acquire_write(2):
            print('Wait for RWLock for too long in WS...Ignoring data')
            return
        if data is not None:
            params = loads(data)
            if params['uapp'] in self.PARAMS_LIST['uapp']:
                self.process_params(params)
                self.create_generator()
        self.LOCK_WS.release()
