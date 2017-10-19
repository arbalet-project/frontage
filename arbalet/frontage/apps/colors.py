#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Color Demonstrator - Arbalet Color Demonstrator

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import random

from utils.tools import Rate
from ._generator import gen_random_flashing, gen_sweep_async, gen_sweep_rand
from .fap import Fap


class Colors(Fap):
    PLAYABLE = False
    PARAMS_LIST = ['dur_min', 'dur_max', 'refresh_rate', 'generator']
    GENERATORS_DICT = {  'random_flashing': gen_random_flashing,
                    'sweep_async': gen_sweep_async,
                    'sweep_rand': gen_sweep_rand }

    def __init__(self):
        Fap.__init__(self)

    def run(self, params):
        self.durations_min = params.get('dur_min', 60)
        self.durations_max = params.get('dur_max', 600)
        self.rate = Rate(params.get('refresh_rate', 50))
        self.colors = params['colors']
        self.generator = self.GENERATORS_DICT[params.get('generator')]

        # Construct all pixel generators
        generators = []
        for h in xrange(self.model.height):
            line = []
            for w in xrange(self.model.width):
                duration = random.randrange(0, self.durations_max-self.durations_min)
                line.append(self.generator(self.durations_min, int((2.0/self.rate.sleep_dur)), duration, self.colors))
            generators.append(line)

        # Browse all pixel generators at each time
        while True:
            with self.model:
                for h in xrange(self.model.height):
                    for w in xrange(self.model.width):
                        try:
                            color = next(generators[h][w])
                        except StopIteration:
                            pass
                        else:
                            self.model.set_pixel(h, w, color)
                            self.send_model()
            self.rate.sleep()
