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
        self.mapping = array([[19, 18, 17, 16, 15, 14, 13, 12, 11, 10,  9,  8,  7,  6,  5,  4,  3, 2,  1],
                              [38, 37, 36, 35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20],
                              [57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41, 40, 39],
                              [71, 70, 69, 68, 67, 66, 65,  0,  0,  0,  0,  0, 64, 63, 62, 61, 60, 59, 58]])


        self.num_pixels = self.mapping.shape[0] * self.mapping.shape[1]
        # Use asyncio or twisted?
        self.hardware_server = socket(AF_INET, SOCK_STREAM)
        #self.hardware_server.settimeout(10.0)  # Non-blocking requests
        self.hardware_server.bind(("0.0.0.0", hardware_port))
        self.hardware_server.listen(1)
        self.running = False

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

    def set_all(self, r, g, b):
        for row in range(self.model.height):
            for col in range(self.model.width):
                self.model[row, col] = r, g, b

    def update(self):
        if self.client is not None:
            with self.model:
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
        if self.hardware_server is not None:
            self.hardware_server.close()

