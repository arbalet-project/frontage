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
from utils.colors import name_to_rgb

class Drawing(Fap):

    def __init__(self, username, userid):
        Fap.__init__(self, username, userid)

    def handle_message(self, data, path=None): # noqa
        if data is None:
            print("Error : message received on websocket is empty.")
        else:
            try:
                pixel = json.loads(data)
            except Exception as e:
                print("Message received in web socket by 'Drawing Fapp' could not be cast as JSON. Message : [{0}]".format(data))
                print(e)

            red = convert_color(pixel.red)
            green = convert_color(pixel.green)
            blue = convert_color(pixel.blue)
            color = (red, green, blue)
            
            try:
                self.model.set_pixel(pixel.x, pixel.y, color)
            except Exception as e:
                print("Message received in web socket by 'Drawing Fapp' is incorrect. Read below for the stack trace.")
                print(e)

    def convert_color(self, simple_color):
        if isinstance(simple_color) is not int:
            print("WARNING : color received is not an int. Try casting it.[color received : {0}]".format(simple_color))
            simple_color = int(simple_color)
        
        if simple_color < 0 or simple_color > 255:
            raise Exception("ERROR : color received should be a value between 0 and 255 but it is [{0}]".format(simple_color))
            
        return simple_color/255.

    def run(self, params, expires_at=None):
        self.start_socket()

