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
        self.PARAMS_LIST = { 'uapp': None,
                    'dur_min': 5,
                    'dur_max': 20 ,
                    'refresh_rate': 50,
                    'colors': []}
        Fap.__init__(self)
        self.generator = gen

    def run(self, params):
        if not self.generator:
            print('GENERATOR NOT DEFINED. ABORDED')
        c_params = None
        if params and (params.get('uapp', False) in self.PARAMS_LIST['uapp']):
            c_params = animations[params['uapp']]
        else:
            raise NameError('uapp not found')
        self.durations_min = params.get('dur_min', c_params.get('dur_min'))
        self.durations_max = params.get('dur_max', c_params.get('dur_max'))
        self.rate = Rate(params.get('refresh_rate', c_params.get('rate')))
        self.colors = []
        for c in params['colors']:
            if isinstance(c, (tuple, list, set)):
                self.colors.append(rgb_to_hsv(c))
            elif c in cnames:
                self.colors.append(name_to_hsv(c))
            else:
                print(str(c) + ' is not a valid color')

        # Construct all pixel generators
        generators = []
        for h in range(self.model.height):
            line = []
            for w in range(self.model.width):
                duration = random.randrange(0, self.durations_max - self.durations_min)
                line.append(self.generator(self.durations_min, int((2.0 / self.rate.sleep_dur)), duration, self.colors))
            generators.append(line)

        # Browse all pixel generators at each time
        while True:
            with self.model:
                for h in range(self.model.height):
                    for w in range(self.model.width):
                        try:
                            color = next(generators[h][w])
                        except StopIteration:
                            pass
                        else:
                            self.model.set_pixel(h, w, color)
                            self.send_model()
            self.rate.sleep()
