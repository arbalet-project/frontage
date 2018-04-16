#!/usr/bin/env python
"""
    Arbalet - ARduino-BAsed LEd Table
    Color Demonstrator - Arbalet Color Demonstrator

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import random

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

    def __init__(self, gen):
        Fap.__init__(self)
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

    def select_colors(self, params, c_params):
        self.colors = []
        param_color = params.get('colors', False)

        # we convert to list if needed
        if param_color and isinstance(param_color, str):
            params['colors'] = [param_color]

        for c in params.get('colors', c_params.get('colors')):
            if isinstance(c, (tuple, list, set)):
                self.colors.append(rgb_to_hsv(c))
            elif c in cnames:
                self.colors.append(name_to_hsv(c))
            else:
                print(str(c) + ' is not a valid color')

    def load_animation(self, params):
        if params and (params.get('uapp', False) in self.PARAMS_LIST['uapp']):
            return animations[params['uapp']]
        else:
            return {}

    def process_params(self, params):
        c_params = self.load_animation(params)

        if self.rate:
            del self.rate
        rate_hz = params.get('refresh_rate', c_params.get('rate'))
        self.rate = Rate(rate_hz)
        self.durations_min = params.get('dur_min', c_params.get('dur_min'))*rate_hz
        self.durations_max = params.get('dur_max', c_params.get('dur_max'))*rate_hz
        self.select_colors(params, c_params)

    def run(self, params, expires_at=None):
        if not self.generator:
            print('GENERATOR NOT DEFINED. ABORTED')
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
                            # print('Error StopIteration')
                            pass
                        except IndexError:
                            # print('Error IndexError')
                            pass
                        else:
                            self.model.set_pixel(h, w, color)
                self.send_model()
            self.rate.sleep()
