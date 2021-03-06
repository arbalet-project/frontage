#!/usr/bin/env python

import sys
import json
import logging
import pika
from os import environ
from artnet import dmx
from os.path import realpath, dirname, join
from db.base import session_factory, engine
from db.models import DimensionsModel, ArtnetModel, DMXModel

"""
Art-Net I UDP broadcasting to all Art-Net nodes 2.xxx.xxx.xxx
Note: UDP doesn't forward over NAT, so running this script from a container needs to bind to the host network:
    docker run artnet --net=host
"""


class ArtNetTransmitter(object):
    FPS = 15
    ARTNET_BROADCAST_IP = "2.255.255.255"
    # Connect on localhost on the host side. Warning: wait-for-it.sh also waits on localhost
    RABBIT_HOST = 'localhost'

    def __init__(self):
        self.logger = logging.getLogger("Artnet")
        self.logger.setLevel(logging.INFO)
        self.channel = None
        self.connection = None
        self.frames = {}  # A different frame of 512 dmx addresses per universe
        # This is the Art-Net mapping [row, col] -> {"universe": 0, "dmx": 511}
        self.mapping = None
        self.dmx = None
        self.num_universes = 0

    def callback(self, ch, method, properties, body):
        raw = json.loads(body.decode('ascii'))
        if self.num_universes > 0:
            for row in range(len(self.mapping)):
                for col in range(len(self.mapping[0])):
                    matches = self.mapping[row][col]
                    # matches should be as such: [{"uni": 0, "dmx": 511}, {"uni": 0, "dmx": 500}, ...]
                    try:
                        r, g, b = raw[row][col]
                    except IndexError:
                        # Might happen if matrix config is ot consistent with Artnet config
                        pass
                    else:
                        for match in matches:
                            universe = match["universe"]
                            dmx = match["dmx"]
                            self.frames[universe][dmx] = min(
                                255, max(0, int(r*255)))
                            self.frames[universe][dmx +
                                                  1] = min(255, max(0, int(g*255)))
                            self.frames[universe][dmx +
                                                  2] = min(255, max(0, int(b*255)))

            for universe in self.frames:
                self.dmx.add(iter([self.frames[universe]]), universe)

    """
    This will declare all existing universes
    """
    def init(self):
        session = session_factory()
        rows = session.query(DimensionsModel).first().rows
        cols = session.query(DimensionsModel).first().cols
        self.mapping = [[[] for c in range(cols)] for r in range(rows)]
        for row in range(rows):
            for col in range(cols):
                artnets = session.query(ArtnetModel).filter_by(
                    row=row, column=col).first()
                if artnets is None:
                    continue
                for dmx_model in artnets.children:
                    dmx_mapping = {}
                    dmx_mapping["universe"] = dmx_model.universe
                    dmx_mapping["dmx"] = dmx_model.address
                    self.mapping[row][col].append(dmx_mapping)
                    universe = dmx_model.universe
                    if universe not in self.frames:
                        # Declare a new universe with 512 DMX addresses = 0
                        self.frames[universe] = [0]*512
        # e.g. universes 4,5 will create universes 0,1,2,3,4,5
        if len(self.frames) == 0:
            raise EnvironmentError("Artnet configuration is not set")
        else:
            self.num_universes = max(self.frames) + 1
        self.dmx = dmx.Controller(
            self.ARTNET_BROADCAST_IP, universes=self.num_universes, fps=self.FPS)
        self.dmx.start()
        self.logger.info("Created {} DMX universes".format(self.num_universes))

    def run(self):
        if 'RABBITMQ_DEFAULT_PASS' not in environ or 'RABBITMQ_DEFAULT_USER' not in environ:
            raise ValueError(
                "The Art-Net transmitter requires RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS in its environment")

        rabbit_host, rabbit_user, rabbit_pwd = self.RABBIT_HOST, environ[
            'RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS']

        credentials = pika.PlainCredentials(rabbit_user, rabbit_pwd)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbit_host, credentials=credentials, heartbeat=60))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(
            exchange='pixels', exchange_type='fanout')

        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pixels', queue=queue_name)

        self.logger.info('Waiting for pixel data...')

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    def close(self):
        if self.channel is not None:
            self.channel.stop_consuming()
        if self.channel is not None:
            self.channel.close()
        if self.connection is not None:
            self.connection.close()
        if self.dmx is not None:
            self.dmx.stop()


if __name__ == '__main__':
    transmitter = ArtNetTransmitter()
    try:
        transmitter.init()
        transmitter.run()
    except KeyboardInterrupt:
        transmitter.logger.warning(
            "Closing all ArtNet transmissions upon request!")
        pass
    finally:
        transmitter.close()
