from __future__ import print_function

from os import environ
from model import Model
from threading import Thread
from server.flaskutils import print_flush

from scheduler_state import SchedulerState
import pika
from utils.red import redis
from utils.tools import Rate


__all__ = ['Frontage']


class Frontage(Thread):
    RATE_HZ = 20

    def __init__(self, height=4, width=19):
        Thread.__init__(self)
        self.model = Model(height, width)
        self.rate = Rate(self.RATE_HZ)

    def __getitem__(self, row):
        return self.model.__getitem__(row)

    def __setitem__(self, key, value):
        with self.model:
            self.model.__setitem__(key, value)

    def set_all(self, r, g, b):
        for row in range(self.model.height):
            for col in range(self.model.width):
                self.model[row, col] = r, g, b

    def erase_all(self):
        self.set_all(0, 0, 0)

    def run(self):
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe([SchedulerState.KEY_MODEL])

        credentials = pika.PlainCredentials(environ.get('RABBITMQ_DEFAULT_USER'), environ.get('RABBITMQ_DEFAULT_PASS'))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbit', credentials=credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='pixels', exchange_type='fanout')

        print("==> Frontage hardware server is up!")
        self.running = True
        while self.running:
            frames = self.pubsub.listen()
            try:
                frame = next(frames)
            except StopIteration:
                pass
            else:
                if frame['type'] == 'message' and frame['data']:
                    data = frame['data']
                    self.model.set_from_json(data)
                    self.channel.basic_publish(exchange='pixels', routing_key='', body=data)
            self.rate.sleep()


    @property
    def is_running(self):
        return self.running

    def close(self):
        self.running = False
        print("==> Frontage Controler Ended. ByeBye")
