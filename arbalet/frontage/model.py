"""
    Arbalet - ARduino-BAsed LEd Table
    Model - Arbalet State

    Store a snapshot of the table state

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import numpy as np
import json
import time

from threading import RLock
from utils.colors import name_to_rgb
from utils.tools import Rate

__all__ = ['Model']


class Model(object):
    # line, column
    def __init__(self, height, width, color=(0.0, 0.0, 0.0)):
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

    def set_pixel(self, h, w, color):
        if isinstance(color, str):
            color = name_to_rgb(color)
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
        m._model = scalar * self._model
        return m

    def json(self):
        return json.dumps(self._model.tolist())

    def set_from_json(self, json_data):
        self._model = np.array(json.loads(json_data))

        return self._model

    def flash(self, duration=4., speed=1.5):
        """
        Blocking and self-locking call flashing the current model on and off (mainly for game over)
        :param duration: Approximate duration of flashing in seconds
        :param rate: Rate of flashing in Hz
        """
        rate = Rate(speed)
        t0 = time.time()
        model_id = 0
        with self._model_lock:
            models = [np.zeros((self.height, self.width, 3)), self._model]

        model_off = False
        while time.time() - t0 < duration or model_off:
            with self._model_lock:
                self._model = models[model_id]
            model_id = (model_id + 1) % 2
            model_off = not model_off
            rate.sleep()
