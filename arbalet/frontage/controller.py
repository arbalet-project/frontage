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
        self.mapping = array([[(6, 19),
                               (6, 22),
                               (6, 25),
                               (6, 28),
                               (6, 31),
                               (6, 34),
                               (6, 37),
                               (6, 40),
                               (6, 43),
                               (7, 49),
                               (7, 46),
                               (7, 43),
                               (7, 40),
                               (7, 37),
                               (7, 34),
                               (7, 31),
                               (7, 28),
                               (7, 25),
                               (7, 22)],
                              [(4, 19),
                               (4, 22),
                               (4, 25),
                               (4, 28),
                               (4, 31),
                               (4, 34),
                               (4, 37),
                               (4, 40),
                               (4, 43),
                               (5, 49),
                               (5, 46),
                               (5, 43),
                               (5, 40),
                               (5, 37),
                               (5, 34),
                               (5, 31),
                               (5, 28),
                               (5, 25),
                               (5, 22)],
                              [(2, 19),
                               (2, 22),
                               (2, 25),
                               (2, 28),
                               (2, 31),
                               (2, 34),
                               (2, 37),
                               (2, 40),
                               (2, 43),
                               (3, 49),
                               (3, 46),
                               (3, 43),
                               (3, 40),
                               (3, 37),
                               (3, 34),
                               (3, 31),
                               (3, 28),
                               (3, 25),
                               (3, 22)],
                              [(0, 19),
                               (0, 22),
                               (0, 25),
                               (0, 28),
                               (0, 31),
                               (0, 34),
                               (0, 37),
                               (0, 40),
                               (0, 43),
                               (1, 49),
                               (1, 46),
                               (1, 43),
                               (1, 40),
                               (1, 37),
                               (1, 34),
                               (1, 31),
                               (1, 28),
                               (1, 25),
                               (1, 22)]])

        self.num_pixels = self.mapping.shape[0] * self.mapping.shape[1]
        self.num_universes = 8
        self.dmx = None
        self.simulator = None

        if simulator:
            self.simulator = Simulator(self.model)

        if artnet:
            # Broadcasting on all Arnet nodes network 2.0.0.0/8
            self.dmx = dmx.Controller("2.255.255.255", universes=self.num_universes) 
            self.data = [[0]*512]*self.num_universes  # self.data[universe][dmx_address] = dmx_value         
            self.dmx.start()

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
        if self.dmx is not None:
            self.dmx.close()

