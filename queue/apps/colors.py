#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Color Demonstrator - Arbalet Color Demonstrator

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import random
import logging

from utils.tools import Rate
from utils.colors import name_to_hsv, cnames, rgb_to_hsv
from .fap import Fap
from ._generator import animations


class Colors(Fap):
    PLAYABLE = False
    ACTIVATED = True
    # GENERATORS_DICT = { 'random_flashing': gen_random_flashing,
    #                     'sweep_async': gen_sweep_async,
    #                     'sweep_rand': gen_sweep_rand }

    def __init__(self, gen, username, userid):
        Fap.__init__(self, username, userid)
        self.rate = None
        self.PARAMS_LIST = {}
        self.generator = gen


    def create_generator(self):
        # Construct all pixel generators
        self.generators = []
        for h in range(self.model.height):
            line = []
            for w in range(self.model.width):
                duration = random.randrange(0, self.durations_max - self.durations_min)
                line.append(self.generator(self.durations_min, int((2.0 / self.rate.sleep_dur)), duration, self.colors))
            self.generators.append(line)

    def load_animation(self, params):
        # Get uapp from Fap name, it designates a generator (not really the animation that we assign to uapp)
        # TODO refacto: the animation dict should contain a list of generators only, the rest are params
        if 'name' in params:
            name = params['name']
            if params or params.get('uapp', False) not in self.PARAMS_LIST['uapp']:
                if name == 'SweepAsync':
                    params['uapp'] = 'swipe'
                elif name == 'RandomFlashing':
                    params['uapp'] = 'flashes'
                elif name == 'SweepRand':
                    params['uapp'] = 'gender'
        return animations[params['uapp']]


    def process_params(self, params):
        c_params = self.load_animation(params)
        rate_hz = params.get('refresh_rate', c_params.get('rate'))
        self.rate = Rate(rate_hz)
        self.durations_min = params.get('dur_min', c_params.get('dur_min'))*rate_hz
        self.durations_max = params.get('dur_max', c_params.get('dur_max'))*rate_hz

        colors = params.get("colors", c_params.get('colors', []))
        if not isinstance(colors, (tuple, list, map)):
            colors = [colors]

        self.colors = []
        for c in colors:
            if isinstance(c, str):
                try:
                    color = name_to_hsv(c.lower())
                except KeyError:
                    color = (0, 0, 0)
            else:
                color = c
            self.colors.append(color)

    def run(self, params, expires_at=None):
        if not self.generator:
            logging.error('GENERATOR NOT DEFINED. ABORTED')
            return
        self.start_socket()

        self.process_params(params)
        self.create_generator()

        # Browse all pixel generators at each time
        while True:
            with self.model:
                for h in range(self.model.height):
                    for w in range(self.model.width):
                        try:
                            color = next(self.generators[h][w])
                        except StopIteration:
                            pass
                        except IndexError:
                            pass
                        else:
                            self.model.set_pixel(h, w, color)
                self.send_model()
            self.rate.sleep()
