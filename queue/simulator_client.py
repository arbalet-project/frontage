"""
    Arbalet - ARduino-BAsed LEd Table
    Simulator - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import sys

import pika
from os import environ
# from scheduler_state import SchedulerState
from pygame import color, event, display, draw, Rect, QUIT
from pygame.time import Clock
from model import Model

__all__ = ['Simulator']


def print_flush(s):
    print(s)
    sys.stdout.flush()

class Simulator(object):
    def __init__(self, row=10, col=20, port=33460):
        factor_sim = 40
        self.clock = Clock()
        self.model = Model(row, col)
        self.sim_width = self.model.width * factor_sim
        self.sim_height = self.model.height * factor_sim
        self.border_thickness = 1
        self.cell_height = factor_sim
        self.cell_width = factor_sim
        self.connection = None
        self.channel = None
        self.display = None
        self.running = False

        # Create the Window, load its title, icon
        environ['SDL_VIDEO_CENTERED'] = '1'

        self.display = display.set_mode((self.sim_width, self.sim_height), 0, 32)
        display.set_caption("Arbalet Frontage simulator", "Arbalet")

    def update(self):
        self.display.lock()
        try:
            for w in range(self.model.width):
                for h in range(self.model.height):
                    pixel = self.model[h, w]
                    self.display.fill(color.Color(int(pixel[0]*255), int(pixel[1]*255), int(pixel[2]*255)),
                                      Rect(w * self.cell_width,
                                           h * self.cell_height,
                                           self.cell_width,
                                           self.cell_height))

            # Draw vertical lines
            for w in range(self.model.width):
                draw.line(self.display, color.Color(40, 40, 40), (w * self.cell_width, 0),
                          (w * self.cell_width, self.sim_height), self.border_thickness)
            # Draw horizontal lines
            for h in range(self.model.height):
                draw.line(self.display, color.Color(40, 40, 40), (0, h * self.cell_height),
                          (self.sim_width, h * self.cell_height), self.border_thickness)

            display.update()
        finally:
            self.display.unlock()
            return True

    def callback(self, ch, method, properties, body):
        self.model.set_from_json(body.decode('ascii'))
        self.update()
        for e in event.get():
            if e.type == QUIT:
                self.close()

    def run(self):
        self.update()
        # These are the public credentials for dev environment
        credentials = pika.PlainCredentials('frontage', 'uHm65hK6]yfabDwUUksqeFDbOu')
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials, heartbeat = 0))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='pixels', exchange_type='fanout')

        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='pixels', queue=queue_name)

        print('Waiting for pixel data.')

        self.channel.basic_consume(queue_name, self.callback)
        self.channel.start_consuming()


    def close(self):
        if self.channel is not None:
            self.channel.stop_consuming()
        if self.channel is not None:
            self.channel.close()
        if self.connection is not None:
            self.connection.close()
        self.display.lock()
        try:
            display.quit()
        finally:
            self.display.unlock()


if __name__ == '__main__':
    simulator = Simulator()
    simulator.run()
