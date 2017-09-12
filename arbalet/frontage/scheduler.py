
from utils.red import redis, redis_get
from controller import Frontage

class Scheduler(object):

    KEY_USABLE = 'frontage_usable'

    def __init__(self, port, hardware=True, simulator=True):
        self.frontage = Frontage(33460, hardware, simulator)  # Blocking until the hardware client connects

    """ Is scheduller on or off ATM ?"""
    @property
    def usable(self):
        val = redis_get(self.KEY_USABLE)
        return val == "True"

    @my_attribute.setter
    def usable(self, value):
        redis.set(self.KEY_USABLE, str(value))