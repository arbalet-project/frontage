from .model import Model
import requests

__all__ = ['Frontage']


class Frontage(object):
    def __init__(self, server, port, timeout=0.5):
        self.model = Model(4, 19)
        self.url = "http://{}:{}/".format(server, port)
        self.timeout = timeout

        # row, column -> DMX address
        self.mapping = [[59, 60, 61, 62, 63, 64, 65,  0,  0,  0,  0,  0, 66, 67, 68, 69, 70, 71, 72],
                        [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58],
                        [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
                        [ 2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]]


    def map(self, row, column):
        return self.mapping[row][column]


