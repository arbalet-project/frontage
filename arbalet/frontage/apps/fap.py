import time

from utils.red import redis
from scheduler_state import SchedulerState
from model import Model
# from rabbit import CHANNEL, RABBIT_CONNECTION
from utils.lock import RWLock
from utils.websock import Websock
from utils.tools import Rate


class Fap(object):
    CODE_CLOSE_APP = 1
    CODE_GAME_OVER = 2
    CODE_EXPIRE = 3
    CODE_EXPIRE_SOON = 4

    PARAMS_LIST = []
    PLAYABLE = False
    ACTIVATED = True
    ENABLE = True
    CNT = 0
    LOCK = RWLock()
    LOCK_WS = RWLock()

    def __init__(self, model=None):
        SchedulerState.set_expire_soon(False)
        self.username = None
        self.max_time = None
        self.params = None

        if not model:
            self.model = Model(4, 19)
        else:
            self.model = model

    def run(self):
        raise NotImplementedError("Fap.run() must be overidden")

    def send_close_app(self):
        Websock.send_data(Fap.CODE_CLOSE_APP, 'CLOSING')

    def send_game_over(self):
        Websock.send_data(Fap.CODE_GAME_OVER, 'GAME_OVER')

    @staticmethod
    def send_expires():
        SchedulerState.set_expire(True)
        Websock.send_data(Fap.CODE_EXPIRE, 'EXPIRE')

    @staticmethod
    def send_expires_soon(timeout_in_sec):
        SchedulerState.set_expire_soon(True)
        Websock.send_data(Fap.CODE_EXPIRE_SOON, timeout_in_sec)

    def start_socket(self):
        self.ws = Websock(self, '0.0.0.0', 8124)
        self.ws.start()
        # start_server = websockets.serve(self._handle_message, '0.0.0.0', 8124)
        # print('====> Start WebSocket')
        # while True:
        #     asyncio.get_event_loop().run_until_complete(start_server)
        #     asyncio.get_event_loop().run_forever()

    def flash(self, duration=4., speed=1.5):
        """
        Blocking and self-locking call flashing the current model on and off (mainly for game over)
        :param duration: Approximate duration of flashing in seconds
        :param rate: Rate of flashing in Hz
        """
        rate = Rate(speed)
        t0 = time.time()
        model_id = 0
        # with self._model_lock:
        models_bck = self.model._model.copy()

        model_off = False
        while time.time() - t0 < duration or model_off:
            # with self._model_lock:
            if model_id:
                self.model.set_all('black')
            else:
                self.model._model = models_bck.copy()

            model_id = (model_id + 1) % 2
            model_off = not model_off
            self.send_model()
            rate.sleep()

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
        self.ws.close()
        time.sleep(0.2)
        print('----CLOSED----')
        # CHANNEL.queue_delete(queue=SchedulerState.KEY_MODEL)
        # RABBIT_CONNECTION.close()
