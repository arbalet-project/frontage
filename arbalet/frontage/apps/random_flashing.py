#!/usr/bin/env python

import random

from utils.tools import Rate
from ._generator import gen_random_flashing
from .colors import Colors


class RandomFlashing(Colors):

    def __init__(self):
        self.PARAMS_LIST['uapp'] = ['flashes']
        Colors.__init__(self, gen_random_flashing)


