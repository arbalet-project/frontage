"""
    Arbalet - ARduino-BAsed LEd Table
    Simulator - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import socket
import struct

from time import sleep
from os.path import dirname, join
#from ...resources.img import __file__ as img_resources_path
from os import environ
from pygame import color, event, display, draw, Rect, error, QUIT
from pygame.image import load_extended
from model import Model

__all__ = ['Simulator']


class Simulator(object):
    def __init__(self, row=4, col=19, port=33460):
        factor_sim = 40
        self.model = Model(row, col)
        self.sim_width = self.model.width*factor_sim
        self.sim_height = self.model.height*factor_sim
        self.border_thickness = 1
        self.cell_height = factor_sim
        self.cell_width = factor_sim
        self.display = None
        self.closed = False

        # Create the Window, load its title, icon
        environ['SDL_VIDEO_CENTERED'] = '1'

        while not self.start_socket(port):
            print('Next connection try in 3 sec')
            sleep(3)

        self.display = display.set_mode((self.sim_width, self.sim_height), 0, 32)
        #try:
        #    self.icon = load_extended(join(dirname(img_resources_path), 'icon.png'))
        #except error:
        #    pass
        #else:
        #    display.set_icon(self.icon)
        display.set_caption("Arbalet Frontage simulator", "Arbalet")

    def start_socket(self, port):
        print('->Start Connecting...')
        print('Port: '+str(port))
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect(("127.0.0.1", port))
        except socket.error, e:
            print(str(e))
            return False
        print('->Connected')

        return True

    def update(self):
        if not self.closed:
            for e in event.get():
                if e.type == QUIT:
                    return False
            self.display.lock()
            try:
                for w in range(self.model.width):
                    for h in range(self.model.height):
                        pixel = self.model[h, w]
                        self.display.fill(color.Color(int(pixel[0]), int(pixel[1]), int(pixel[2])),
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

    def raw_to_model(self, raw):
        for row in range(self.model.height):
            for col in range(self.model.width):
                current_cell = row*self.model.width+col
                current_cell = current_cell*4
                self.model[row, col] = raw[current_cell+1:current_cell+4]

    def run(self):
        while True:

            resp = self.client.recv(304)
            if resp != "":
                raw = struct.unpack("!{}B".format(76*4), resp)
                self.raw_to_model(raw)
                self.update()
            # sleep(0.005)


    def close(self):
        if not self.closed:
            self.display.lock()
            try:
                display.quit()
                self.closed = True
            finally:
                self.display.unlock()

if __name__ == '__main__':
    simulator = Simulator()
    simulator.run()