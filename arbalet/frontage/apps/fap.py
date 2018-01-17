import time

from utils.red import redis
from scheduler_state import SchedulerState
from model import Model
# from rabbit import CHANNEL, RABBIT_CONNECTION
from utils.lock import RWLock
from utils.websock import Websock


class Fap(object):
    PARAMS_LIST = []
    PLAYABLE = False
    ACTIVATED = True
    ENABLE = True
    CNT = 0
    LOCK = RWLock()

    def __init__(self, model=None):
        self.username = None
        self.max_time = None
        self.params = None

        if not model:
            self.model = Model(4, 19)
        else:
            self.model = model

    def run(self):
        raise NotImplementedError("Fap.run() must be overidden")

    def start_socket(self):
        self.ws = Websock(self, '0.0.0.0', 8124)
        self.ws.start()
        # start_server = websockets.serve(self._handle_message, '0.0.0.0', 8124)
        # print('====> Start WebSocket')
        # while True:
        #     asyncio.get_event_loop().run_until_complete(start_server)
        #     asyncio.get_event_loop().run_forever()

    def send_model(self):
        # self.CNT += 1
        # print(self.CNT)
        if not self.LOCK.acquire_write(2):
            print('Wait for RWLock for too long in Bufferize...Stopping')
            return
        redis.publish(SchedulerState.KEY_MODEL, self.model.json())

        # CHANNEL.basic_publish(exchange='',
        #     routing_key=SchedulerState.KEY_MODEL,
        #     body=self.model.json())
        # redis.set(SchedulerState.KEY_MODEL, self.model.json())

        self.LOCK.release()

    def jsonify(self):
        struct = {}
        struct['name'] = self.__class__.__name__
        struct['params'] = self.params
        struct['params_list'] = self.PARAMS_LIST
        struct['user'] = self.username
        struct['playable'] = self.PLAYABLE
        struct['activated'] = self.ACTIVATED
        struct['max_time'] = self.max_time
        return struct

    def __del__(self):
        print('----CLOSE----')
        time.sleep(0.2)
        # CHANNEL.queue_delete(queue=SchedulerState.KEY_MODEL)
        # RABBIT_CONNECTION.close()
