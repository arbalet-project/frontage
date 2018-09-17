#!/usr/bin/env python
"""
    Copyright 2018:
        Bastien Meunier
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html

    Arbalet - ARduino-BAsed LEd Table
    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import random
from json import loads

from apps.fap import Fap
from apps.actions import Actions
from utils.tools import Rate
from utils.colors import name_to_rgb, rgb_to_hsv, color255_to_color

class Drawing(Fap):

    def __init__(self, username, userid):
        self.rate = Rate(2)
        Fap.__init__(self, username, userid)

    def handle_message(self, data, path=None): # noqa
        if data is None:
            print("Error : message received on websocket is empty.")
        else:
            print(data)

            pixel = data.pixel
            color = data.color

            try:
                self.model.set_pixel(pixel.x, pixel.y, array(color255_to_color(color.red, color.green, color.blue)))
            except Exception as e:
                print("Message received in web socket by 'Drawing Fapp' is incorrect. Read below for the stack trace.")
                print(e)

    def run(self, params, expires_at=None):
        self.start_socket()
        while True:
            self.send_model()
            self.rate.sleep()

