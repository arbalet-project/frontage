#!/usr/bin/env python

"""
Arbalet Frontage simulator
Run this simulator with the dev environment directly on the host (not in a container):
    ~/frontage/simulator$ python3 simulator.py 
If no window opens, it means that no pixel data is received, e.g. rabbitMQ pixels channel is not emitting data
"""

import sys
import json
import logging
import pika
from threading import RLock
from os import environ
from os.path import realpath, dirname, join
from pygame import color, event, display, image, draw, Rect, QUIT

class Simulator(object):
    CELL_HEIGHT = 50
    CELL_WIDTH = 50
    RABBIT_HOST = 'localhost'

    def __init__(self):
        self.lock = RLock()
        self.width = 0
        self.height = 0
        self.logger = logging.getLogger("Simulator")
        self.logger.setLevel(logging.INFO)
        self.channel = None
        self.connection = None
        self.opened = False

    def callback(self, ch, method, properties, body):
        raw = json.loads(body.decode('ascii'))

        # Open window if necessary
        if not self.opened:
            self.height = len(raw)
            self.width = len(raw[0]) if self.height > 0 else 0
            self.open()
        else:
            with self.lock:
                for row in range(self.height):
                    for col in range(self.width):
                        r, g, b = map(lambda x: min(255, max(0, int(x*256))), raw[row][col])
                        self.display.fill(color.Color(r, g, b),
                                            Rect(col * self.CELL_WIDTH,
                                                row * self.CELL_HEIGHT,
                                                self.CELL_WIDTH,
                                                self.CELL_HEIGHT))
                # Draw vertical lines
                for w in range(self.width):
                    draw.line(self.display, color.Color(40, 40, 40), (w * self.CELL_WIDTH, 0),
                                (w * self.CELL_WIDTH, self.sim_height), self.border_thickness)
                # Draw horizontal lines
                for h in range(self.height):
                    draw.line(self.display, color.Color(40, 40, 40), (0, h * self.CELL_HEIGHT),
                                (self.sim_width, h * self.CELL_HEIGHT), self.border_thickness)
                display.update()

            for e in event.get():
                if e.type == QUIT:
                    self.close()

    def open(self):
        # Create the Window, load its title, icon
        environ['SDL_VIDEO_CENTERED'] = '1'

        self.sim_width = self.width * self.CELL_WIDTH
        self.sim_height = self.height * self.CELL_HEIGHT
        self.border_thickness = 2
        path_icon = join(realpath(dirname(__file__)), "icon.png")
        icon = image.load(path_icon)
        self.display = display.set_mode((self.sim_width, self.sim_height), 0, 32)
        display.set_caption("Arbalet Frontage simulator [{}x{}]".format(self.height, self.width), "Arbalet")
        display.set_icon(icon)
        display.update()

        self.opened = True

    def run(self):
        # Connect with default for the dev environment
        rabbit_host, rabbit_user, rabbit_pwd = self.RABBIT_HOST, 'frontage', 'uHm65hK6]yfabDwUUksqeFDbOu'

        credentials = pika.PlainCredentials(rabbit_user, rabbit_pwd)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, credentials=credentials, heartbeat = 10))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='pixels', exchange_type='fanout')

        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pixels', queue=queue_name)

        self.logger.info('Waiting for pixel data in order to open the simulation window...')

        self.channel.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()

    def close(self):
        with self.lock:
            if self.channel is not None:
                self.channel.close()
                self.channel = None
            if self.connection is not None:
                self.connection.close()
                self.connection = None
            if self.opened:
                display.quit()
                self.opened = False

if __name__ == '__main__':
    sim = Simulator()
    try:
        sim.run()
    except KeyboardInterrupt:
        pass
    finally:
        sim.close()