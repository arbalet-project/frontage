"""
    Arbalet - ARduino-BAsed LEd Table
    Simulator - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from socket import *
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
        self.start_socket(port)

        self.display = display.set_mode((self.sim_width, self.sim_height), 0, 32)
        #try:
        #    self.icon = load_extended(join(dirname(img_resources_path), 'icon.png'))
        #except error:
        #    pass
        #else:
        #    display.set_icon(self.icon)
        display.set_caption("Arbalet Frontage simulator", "Arbalet")

    def start_socket(self, port):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.connect(("127.0.0.1", port))

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
    def run(self):
        while True:
            sleep(0.005)


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