from __future__ import print_function 

from .model import Model
from .simulator import Simulator
from threading import Thread
from socket import *
from struct import pack
from numpy import array
from pygame.time import Clock

import sys

__all__ = ['Frontage']


class Frontage(Thread):
    def __init__(self, hardware_port, hardware=True, simulator=True):
        super(Frontage, self).__init__()
        self.model = Model(4, 19)
        self.clock = Clock()

        # row, column -> DMX address
        self.mapping = array([[59, 60, 61, 62, 63, 64, 65,  0,  0,  0,  0,  0, 66, 67, 68, 69, 70, 71, 72],
                              [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58],
                              [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
                              [ 2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]])

        self.num_pixels = self.mapping.shape[0] * self.mapping.shape[1]
        # Use asyncio or twisted?
        self.hardware_server = socket(AF_INET, SOCK_STREAM)
        #self.hardware_server.settimeout(10.0)  # Non-blocking requests
        self.hardware_server.bind(("127.0.0.1", hardware_port))
        self.hardware_server.listen(1)
        self.running = False
        self.needs_update = True

        if simulator:
            self.simulator = Simulator(self.model)
        else:
            self.simulator = None

        if hardware:
            print("Waiting Hardware TCP client connection...", file=sys.stderr)
            self.client, self.address = self.hardware_server.accept()
            print("Client {}:{} connected!".format(self.address[0], self.address[1]), file=sys.stderr)
        else:
            self.client, self.address = None, None

    def map(self, row, column):
        return self.mapping[row][column]

    def __getitem__(self, row):
        return self.model.__getitem__(row)

    def __setitem__(self, key, value):
        with self.model:
            self.model.__setitem__(key, value)
            self.needs_update = True

    def update(self):
        if self.client is not None:
            with self.model:
                if self.needs_update:
                    data_frame = []
                    with self.model:
                        for row in range(self.model.height):
                            for col in range(self.model.width):
                                led = self.mapping[row, col]
                                r, g, b = self.model[row, col]
                                data_frame.append(led)
                                data_frame.append(r)
                                data_frame.append(g)
                                data_frame.append(b)
                    command = pack("!{}B".format(self.num_pixels * 4), *data_frame)
                    self.client.send(command)
                    self.needs_update = False

        if self.simulator is not None:
            self.running = self.simulator.update()

    def run(self):
        self.running = True
        try:
            while self.running:
                self.update()
                self.clock.tick(20)
        finally:
            self.close()

    def close(self):
        if self.simulator is not None:
            self.simulator.close()
