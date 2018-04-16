from __future__ import print_function

from socket import *
from struct import pack
from model import Model
from pygame.time import Clock
from threading import Thread
from server.flaskutils import print_flush

from scheduler_state import SchedulerState
# from rabbit import CHANNEL, QUEUE_OBJ
from utils.red import redis

__all__ = ['Frontage']


class Frontage(Thread):
    CNT = 0

    def __init__(self, hardware_port=33640, hardware=True, width=19, height=4):
        Thread.__init__(self)
        self.model = Model(height, width)
        self.hardware_port = hardware_port
        self.hardware = hardware
        self.clock = Clock()
        self.client, self.address = None, None
        self.num_pixels = width * height

    def start_server(self):
        # Use asyncio or twisted?
        self.hardware_server = socket(AF_INET, SOCK_STREAM)
        # self.hardware_server.settimeout(10.0)  # Non-blocking requests
        self.hardware_server.bind(("0.0.0.0", self.hardware_port))
        self.hardware_server.listen(1)
        # self.start_rabbit()
        if self.hardware:
            print_flush("Waiting Hardware TCP client connection...")
            print_flush(self.hardware_port)
            self.client, self.address = self.hardware_server.accept()
            print_flush(
                "Client {}:{} connected!".format(
                    self.address[0],
                    self.address[1]))
            self.update()

        print_flush("====> START STATE")

    def map(self, row, column):
        return self.mapping[row][column]

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

    def handle_model_msg(self, channel, method, properties, body):
        # print('[MODEL-QUEUE] Received data')
        # self.CNT += 1
        # print('--->'+str(self.CNT))
        # print("---")
        # print(QUEUE_OBJ.method.message_count)

        self.model.set_from_json(body)
        self.update()

    def run(self):
        print("==> Starting Frontage hardware server...")
        self.start_server()
        print("==> Frontage hardware server is up!")
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe([SchedulerState.KEY_MODEL])

        try:
            # CHANNEL.basic_qos(prefetch_count=1)
            # CHANNEL.basic_consume(self.handle_model_msg,
            #   queue=SchedulerState.KEY_MODEL,
            #   no_ack=True)

            # # start consuming (blocks)
            # CHANNEL.start_consuming()
            for item in self.pubsub.listen():
                if item['type'] == 'message' and item['data']:
                    self.model.set_from_json(item['data'])
                    self.update()
        finally:
            self.close()

    def update(self):
        if self.client is not None:
            with self.model:
                data_frame = []
                with self.model:
                    for row in range(self.model.height):
                        for col in range(self.model.width):
                            r, g, b = self.model[row, col]
                            data_frame.append(min(255, max(0, int(r * 255))))
                            data_frame.append(min(255, max(0, int(g * 255))))
                            data_frame.append(min(255, max(0, int(b * 255))))
                try:
                    command = pack(
                        "!{}B".format(
                            self.num_pixels * 3),
                        *data_frame)
                    self.client.send(command)
                except Exception as e:
                    print_flush(str(e))
                    print_flush('=> Deconnected from client')
                    print_flush('=> Wait for new client connection')
                    self.start_server()

    def close(self):
        print("==> Frontage Controler Ended. ByeBye")
        if self.hardware_server is not None:
            self.hardware_server.close()
        # if RABBIT_CONNECTION:
        #      RABBIT_CONNECTION.close()
