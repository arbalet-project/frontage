#!/usr/bin/env python

from ._generator import gen_random_flashing
from .colors import Colors
from json import loads
from server.flaskutils import print_flush


class RandomFlashing(Colors):

    def __init__(self, username, userid):
        Colors.__init__(self, gen_random_flashing, username, userid)
        print_flush("Init of Rand_FLASH", self.model.height, self.model.width)
        self.PARAMS_LIST['uapp'] = ['flashes']


    def handle_message(self, data, path=None): # noqa
        if not self.LOCK_WS.acquire_write(2):
            print('Wait for RWLock for too long in WS...Ignoring data')
            return
        if data is not None:
            params = loads(data)
            params['uapp'] = 'flashes'
            self.process_params(params)
            self.create_generator()
        self.LOCK_WS.release()

    def run(self, params, expires_at=None):
        if not params:
            params = {}
        params['uapp'] = 'flashes'
        Colors.run(self, params, expires_at)
