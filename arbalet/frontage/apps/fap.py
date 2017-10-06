
from utils.red import redis, redis_get
from scheduler_state import SchedulerState
from model import Model
from rabbit import CHANNEL

class Fap(object):
    PARAMS_LIST = []
    PLAYABLE = False
    ENABLE = True

    def __init__(self, model=None):
        self.username = None
        self.max_time = None
        self.params = None

        if not model:
            self.model = Model(4, 19)
        else:
            self.model = model


    def send_model(self):
        CHANNEL.basic_publish(exchange='',
            routing_key=SchedulerState.KEY_MODEL,
            body=self.model.json())
        # redis.set(SchedulerState.KEY_MODEL, self.model.json())

    def jsonify(self):
        struct = {}
        struct['name'] = self.__class__.__name__
        struct['params'] = self.params
        struct['params_list'] = self.PARAMS_LIST
        struct['user'] = self.username
        struct['playable'] = self.PLAYABLE
        struct['max_time'] = self.max_time
        return struct