import pika
import logging
from os import environ
from model import Model
from numpy import array
from artnet import dmx


__all__ = ['ArtnetClient']


class ArtnetClient(object):
    def __init__(self, col=19, row=4):
        self.model = Model(row, col)

         # row, column -> (DMX universe, DMX address)
        self.mapping = array([[[ 7, 18],
                                [ 7, 21],
                                [ 7, 24],
                                [ 7, 27],
                                [ 7, 30],
                                [ 7, 33],
                                [ 7, 36],
                                [ 7, 39],
                                [ 6, 51],
                                [ 6, 48],
                                [ 6, 45],
                                [ 6, 42],
                                [ 6, 39],
                                [ 6, 36],
                                [ 6, 33],
                                [ 6, 30],
                                [ 6, 27],
                                [ 6, 24],
                                [ 6, 21]],
                               [[ 5, 18],
                                [ 5, 21],
                                [ 5, 24],
                                [ 5, 27],
                                [ 5, 30],
                                [ 5, 33],
                                [ 5, 36],
                                [ 5, 39],
                                [ 4, 51],
                                [ 4, 48],
                                [ 4, 45],
                                [ 4, 42],
                                [ 4, 39],
                                [ 4, 36],
                                [ 4, 33],
                                [ 4, 30],
                                [ 4, 27],
                                [ 4, 24],
                                [ 4, 21]],
                               [[ 2, 18],
                                [ 2, 21],
                                [ 2, 24],
                                [ 2, 27],
                                [ 2, 30],
                                [ 2, 33],
                                [ 2, 36],
                                [ 2, 39],
                                [ 2, 42],
                                [ 3, 48],
                                [ 3, 45],
                                [ 3, 42],
                                [ 3, 39],
                                [ 3, 36],
                                [ 3, 33],
                                [ 3, 30],
                                [ 3, 27],
                                [ 3, 24],
                                [ 3, 21]],
                               [[ 0, 18],
                                [ 0, 21],
                                [ 0, 24],
                                [ 0, 27],
                                [ 0, 30],
                                [ 0, 33],
                                [ 0, 36],
                                [ 0, 39],
                                [ 0, 42],
                                [ 1, 48],
                                [ 1, 45],
                                [ 1, 42],
                                [ 1, 39],
                                [ 1, 36],
                                [ 1, 33],
                                [ 1, 30],
                                [ 1, 27],
                                [ 1, 24],
                                [ 1, 21]]])

        self.back_mapping = array([[(6, 18),
                                  (6, 15),
                                  (6, 12),
                                  (6, 9),
                                  (6, 6),
                                  (6, 3),
                                  (6, 0),
                                  (7, 0),
                                  (7, 3),
                                  (7, 6),
                                  (7, 9),
                                  (7, 12),
                                  (7, 15)],
                                 [(4, 18),
                                  (4, 15),
                                  (4, 12),
                                  (4, 9),
                                  (4, 6),
                                  (4, 3),
                                  (4, 0),
                                  (5, 6),
                                  (5, 3),
                                  (5, 0),
                                  (5, 9),
                                  (5, 12),
                                  (5, 15)],
                                 [(3, 18),
                                  (3, 15),
                                  (3, 12),
                                  (3, 9),
                                  (3, 6),
                                  (3, 3),
                                  (3, 0),
                                  (2, 0),
                                  (2, 3),
                                  (2, 6),
                                  (2, 9),
                                  (2, 12),
                                  (2, 15)],
                                 [(1, 18),
                                  (1, 15),
                                  (1, 12),
                                  (1, 9),
                                  (1, 6),
                                  (1, 3),
                                  (1, 0),
                                  (0, 0),
                                  (0, 3),
                                  (0, 6),
                                  (0, 9),
                                  (0, 12),
                                  (0, 15)]])

        self.num_pixels = row*col
        self.num_universes = 8
        self.dmx = None
        self.data = [[0]*512 for u in range(self.num_universes)]  # self.data[universe][dmx_address] = dmx_value
        credentials = pika.PlainCredentials(environ['RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS'])
        self.params = pika.ConnectionParameters(host='localhost', credentials=credentials, connection_attempts = 1000)

    def start_dmx(self):
        if self.dmx is None:
            # Broadcasting on all Arnet nodes network 2.0.0.0/8
            self.dmx = dmx.Controller("2.255.255.255", universes=self.num_universes, fps=15)
            self.dmx.start()

    def close_dmx(self):
        if self.dmx is not None:
            self.dmx.stop()
            self.dmx = None

    def callback(self, ch, method, properties, body):
        self.model.set_from_json(body.decode('ascii'))
        if self.dmx is not None:
            for row in range(self.model.height):
                for col in range(self.model.width):
                    universe, address = self.mapping[row, col]
                    r, g, b = self.model[row, col]
                    self.data[universe][address] = min(255, max(0, int(r*255)))
                    self.data[universe][address+1] = min(255, max(0, int(g*255)))
                    self.data[universe][address+2] = min(255, max(0, int(b*255)))
                    #if row==0 and col==0: print(universe, address, r, g, b)

            for row in range(self.back_mapping.shape[0]):
                for col in range(self.back_mapping.shape[1]):
                    universe, address = self.back_mapping[row, col]
                    r, g, b = self.model[row, col + (6 if col > 6 else 0)]
                    self.data[universe][address] = min(255, max(0, int(r*255)))
                    self.data[universe][address+1] = min(255, max(0, int(g*255)))
                    self.data[universe][address+2] = min(255, max(0, int(b*255)))

            for universe in range(len(self.data)):
                self.dmx.add(iter([self.data[universe]]), universe)

    def run(self):
        self.start_dmx()
        try:
            connection = pika.BlockingConnection(self.params)
            self.channel = connection.channel()

            self.channel.exchange_declare(exchange='pixels', exchange_type='fanout')

            result = self.channel.queue_declare(exclusive=True, arguments={"x-max-length": 1})
            queue_name = result.method.queue

            self.channel.queue_bind(exchange='pixels', queue=queue_name)
            self.channel.basic_consume(self.callback, queue=queue_name, no_ack=True)

            print('Waiting for pixel data on queue "{}".'.format(queue_name))
            self.channel.start_consuming()
        except Exception as e:
            self.close_dmx()
            raise e



if __name__ == '__main__':
    artnet = ArtnetClient()
    logger = logging.getLogger("artnet.dmx")
    logger.setLevel(logging.ERROR)
    artnet.run()

