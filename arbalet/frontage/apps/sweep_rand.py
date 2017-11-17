#!/usr/bin/env python

import random

from utils.tools import Rate
from ._generator import gen_sweep_rand
from .colors import Colors


class SweepRand(Colors):

    def __init__(self):
        Colors.__init__(self, gen_sweep_rand)
        self.PARAMS_LIST['uapp'] = ['african', 'gender', 'teddy', 'warm']


