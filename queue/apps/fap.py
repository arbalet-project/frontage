import time
import pika
import logging

from os import environ
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
    CODE_TETRIS_CLEARED_ROW = 10
    CODE_SNAKE_ATE_APPLE = 11

    PARAMS_LIST = []
    PLAYABLE = False
    ACTIVATED = True
    ENABLE = True
    LOCK = RWLock()
    LOCK_WS = RWLock()

    def __init__(self, username, userid):
        SchedulerState.set_expire_soon(False)
        self.max_time = None
        self.params = None
        self.username = username
        self.userid = userid
        self.ws = None
        self.model = Model(SchedulerState.get_rows(), SchedulerState.get_cols())

        credentials = pika.PlainCredentials(environ.get('RABBITMQ_DEFAULT_USER'), environ.get('RABBITMQ_DEFAULT_PASS'))
        self.connection_params = pika.ConnectionParameters(host='rabbit', credentials=credentials, connection_attempts = 100, heartbeat = 0)
        self.connection = pika.BlockingConnection(self.connection_params)
        #####   Channel used for emiting  model to scheduler
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='model', exchange_type='fanout')

    def run(self):
        raise NotImplementedError("Fap.run() must be overidden")

    def send_close_app(self):
        Websock.send_data(Fap.CODE_CLOSE_APP, 'CLOSING', self.username, self.userid)

    def send_game_over(self):
        Websock.send_data(Fap.CODE_GAME_OVER, 'GAME_OVER', self.username, self.userid)

    def send_message(self, code):
        Websock.send_data(code, 'Gamelife message', self.username, self.userid)

    @staticmethod
    def send_expires(username='', userid=''):
        SchedulerState.set_expire(True)
        Websock.send_data(Fap.CODE_EXPIRE, 'EXPIRE', username, userid)

    @staticmethod
    def send_expires_soon(timeout_in_sec, username='', userid=''):
        SchedulerState.set_expire_soon(True)
        Websock.send_data(Fap.CODE_EXPIRE_SOON, timeout_in_sec, username, userid)

    def start_socket(self):
        self.ws = Websock(self, '0.0.0.0', 33406)
        self.ws.start()

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
        if not self.LOCK.acquire_write(2):
            logging.error('Wait for RWLock for too long in Bufferize...Stopping')
            return
        try:
            self.channel.basic_publish(exchange='model', routing_key='', body=self.model.json())
        except Exception as e:
            logging.error('FAP Cannot send model to scheduler')
            raise e
        finally:
            self.LOCK.release()

    def jsonify(self):
        struct = {}
        struct['name'] = self.__class__.__name__
        struct['params'] = self.params
        struct['params_list'] = self.PARAMS_LIST
        struct['playable'] = self.PLAYABLE
        struct['activated'] = self.ACTIVATED
        return struct

    def close(self):
        if self.channel is not None:
            self.channel.close()
        if self.connection is not None:
            self.connection.close()
        if self.ws is not None:
            self.ws.close()
            time.sleep(0.2)
