"""
    Arbalet - ARduino-BAsed LEd Table
    Simulator - Arbalet Simulator

    Simulate an Arbalet table

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
from os.path import dirname, join
#from ...resources.img import __file__ as img_resources_path
from os import environ
from pygame import color, event, display, draw, Rect, error, QUIT
from pygame.time import Clock
from pygame.image import load_extended
from threading import Thread

__all__ = ['Simulator']


class Simulator(Thread):
    def __init__(self, model):
        super(Simulator, self).__init__()
        factor_sim = 40   # TODO autosize
        self.clock = Clock()
        self.model = model
        self.sim_width = self.model.width*factor_sim
        self.sim_height = self.model.height*factor_sim
        self.border_thickness = 1
        self.cell_height = factor_sim
        self.cell_width = factor_sim
        self.display = None
        self.running = False

        # Create the Window, load its title, icon
        environ['SDL_VIDEO_CENTERED'] = '1'

        self.display = display.set_mode((self.sim_width, self.sim_height), 0, 32)
        self.update()
        #try:
        #    self.icon = load_extended(join(dirname(img_resources_path), 'icon.png'))
        #except error:
        #    pass
        #else:
        #    display.set_icon(self.icon)
        display.set_caption("Arbalet Frontage simulator", "Arbalet")

    def run(self):
        self.running = True
        while self.running:
            for e in event.get():
                if e.type == QUIT:
                    self.display.lock()
                    self.running = False
                    display.quit()
                    self.display.unlock()
            self.clock.tick(20)

    def update(self):
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

