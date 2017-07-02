"""
    Arbalet - ARduino-BAsed LEd Table
    Model - Arbalet State

    Store a snapshot of the table state

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import numpy as np
from threading import RLock


__all__ = ['Model']


class Model(object):
    # line, column
    def __init__(self, height, width, color=(0, 0, 0)):
        self.height = height
        self.width = width
        self.font = None

        self._model_lock = RLock()
        self._model = np.tile(color, (height, width, 1)).astype(float)

    def __getitem__(self, item):
        return self._model[item]

    def __setitem__(self, key, value):
        self._model[key] = value

    def set_line(self, h, color):
        for w in range(self.width):
            self._model[h, w] = color

    def set_column(self, w, color):
        for h in range(self.height):
            self._model[h, w] = color

    def set_all(self, color):
        for w in range(self.width):
            for h in range(self.height):
                self._model[h, w] = color

    def __enter__(self):
        self._model_lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._model_lock.release()

    def __add__(self, other):
        m = Model(self.height, self.width)
        m._model = self._model + other._model
        return m

    def __eq__(self, other):
        return (self._model == other._model).all()

    def __sub__(self, other):
        m = Model(self.height, self.width)
        m._model = self._model - other._model
        return m

    def __repr__(self):
        return repr(self._model)

    def __str__(self):
        return str(self._model)

    def __mul__(self, scalar):
        m = Model(self.height, self.width)
        m._model = scalar*self._model
        return m
