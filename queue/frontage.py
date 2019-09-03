from __future__ import print_function

from os import environ
from model import Model
from db.models import DimensionsModel
from threading import Thread

from scheduler_state import SchedulerState
import pika
from utils.tools import Rate


__all__ = ['Frontage']


class Frontage(Thread):
    RATE_HZ = 30
    FADE_OUT_NUM_FRAMES = 20

    def __init__(self, height=4, width=19):
        Thread.__init__(self)
        self.setDaemon(True)
        DimensionsModel()
        self.model = Model(height, width)
        self.rate = Rate(self.RATE_HZ)
        self.frontage_running = False
        self.fade_out_idx = 0
        self.connection = None
        self.channel = None

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

    def fade_out(self):
        self.fade_out_idx = self.FADE_OUT_NUM_FRAMES

    def run(self):
        credentials = pika.PlainCredentials(environ.get('RABBITMQ_DEFAULT_USER'), environ.get('RABBITMQ_DEFAULT_PASS'))
        self.connection_params = pika.ConnectionParameters(host='rabbit', credentials=credentials, connection_attempts = 100, heartbeat = 0)
        self.connection = pika.BlockingConnection(self.connection_params)

        #####    Receive model from apps
        self.channel_app_model = self.connection.channel()
        self.channel_app_model.exchange_declare(exchange='model', exchange_type='fanout')
        result = self.channel_app_model.queue_declare(queue='', exclusive=True, arguments={"x-max-length": 1})
        queue_name = result.method.queue
        self.channel_app_model.queue_bind(exchange='model', queue=queue_name)

        #####   Emit model to end frame
        self.channel_pixels = self.connection.channel()
        self.channel_pixels.exchange_declare(exchange='pixels', exchange_type='fanout')
        self.frontage_running = True

        while self.frontage_running:
            # ASYNCHRONOUS END FRAME UPDATE LOOP
            method, properties, body = self.channel_app_model.basic_get(queue=queue_name)
            if self.fade_out_idx > 1:
                self.model = self.model.__mul__(0.9)
                self.fade_out_idx -= 1
            elif self.fade_out_idx == 1:
                self.model = self.model.__mul__(0)
                self.fade_out_idx = 0
            elif body is not None:
                self.model.set_from_json(body)
            if self.frontage_running:
                self.channel_pixels.basic_publish(exchange='pixels', routing_key='', body=self.model.json())
                self.rate.sleep()

        # Closing
        if self.channel is not None:
            self.channel.close()
        if self.connection is not None:
            self.connection.close()

    @property
    def is_running(self):
        return self.frontage_running

    def close(self):
        self.frontage_running = False
