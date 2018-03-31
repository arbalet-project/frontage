from __future__ import print_function 

from .model import Model
from .simulator import Simulator
from threading import Thread
from socket import *
from struct import pack
from numpy import array
from pygame.time import Clock
from artnet import dmx

import sys

__all__ = ['Frontage']


class Frontage(Thread):
    def __init__(self, hardware_port, artnet=True, simulator=True):
        Thread.__init__(self)
        self.clock = Clock()
        self.model = Model(4, 19)

        # row, column -> (DMX universe, DMX address)
        self.mapping = array([[[ 7, 18],
                                [ 7, 21],
                                [ 7, 24],
                                [ 7, 27],
                                [ 7, 30],
                                [ 7, 33],
                                [ 7, 36],
                                [ 7, 39],
                                [ 6, 51],
                                [ 6, 48],
                                [ 6, 45],
                                [ 6, 42],
                                [ 6, 39],
                                [ 6, 36],
                                [ 6, 33],
                                [ 6, 30],
                                [ 6, 27],
                                [ 6, 24],
                                [ 6, 21]],

                               [[ 5, 18],
                                [ 5, 21],
                                [ 5, 24],
                                [ 5, 27],
                                [ 5, 30],
                                [ 5, 33],
                                [ 5, 36],
                                [ 5, 39],
                                [ 4, 51],
                                [ 4, 48],
                                [ 4, 45],
                                [ 4, 42],
                                [ 4, 39],
                                [ 4, 36],
                                [ 4, 33],
                                [ 4, 30],
                                [ 4, 27],
                                [ 4, 24],
                                [ 4, 21]],

                               [[ 2, 18],
                                [ 2, 21],
                                [ 2, 24],
                                [ 2, 27],
                                [ 2, 30],
                                [ 2, 33],
                                [ 2, 36],
                                [ 2, 39],
                                [ 2, 42],
                                [ 3, 48],
                                [ 3, 45],
                                [ 3, 42],
                                [ 3, 39],
                                [ 3, 36],
                                [ 3, 33],
                                [ 3, 30],
                                [ 3, 27],
                                [ 3, 24],
                                [ 3, 21]],

                               [[ 0, 18],
                                [ 0, 21],
                                [ 0, 24],
                                [ 0, 27],
                                [ 0, 30],
                                [ 0, 33],
                                [ 0, 36],
                                [ 0, 39],
                                [ 0, 42],
                                [ 1, 48],
                                [ 1, 45],
                                [ 1, 42],
                                [ 1, 39],
                                [ 1, 36],
                                [ 1, 33],
                                [ 1, 30],
                                [ 1, 27],
                                [ 1, 24],
                                [ 1, 21]]])

        self.num_pixels = self.mapping.shape[0] * self.mapping.shape[1]
        self.num_universes = 8
        self.dmx = None
        self.simulator = None

        if simulator:
            self.simulator = Simulator(self.model)

        if artnet:
            # Broadcasting on all Arnet nodes network 2.0.0.0/8
            self.dmx = dmx.Controller("2.255.255.255", universes=self.num_universes) 
            self.data = [[0]*512 for u in range(self.num_universes)]  # self.data[universe][dmx_address] = dmx_value         
            self.dmx.start()  # Peut lever Network is unreachable

    def map(self, row, column):
        return self.mapping[row][column]

    def __getitem__(self, row):
        return self.model.__getitem__(row)

    def __setitem__(self, key, value):
        with self.model:
            self.model.__setitem__(key, value)

    def set_all(self, r, g, b):
        for row in range(self.model.height):
            for col in range(self.model.width):
                self.model[row, col] = r, g, b

    def update(self):
        if self.dmx is not None:
            with self.model:
                for row in range(self.model.height):
                    for col in range(self.model.width):
                        universe, address = self.mapping[row, col]

                        r, g, b = map(int, self.model[row, col])
                        self.data[universe][address] = r
                        self.data[universe][address+1] = g
                        self.data[universe][address+2] = b
            for universe in range(len(self.data)):
                self.dmx.add(iter([self.data[universe]]), universe)


    def run(self):
        self.running = True
        try:
            while self.running:
                if self.simulator is not None:
                    self.running = self.simulator.update()
                self.clock.tick(20)
        finally:
            self.close()

    def close(self):
        if self.simulator is not None:
            self.simulator.close()


