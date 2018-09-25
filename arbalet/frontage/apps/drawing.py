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
from utils.colors import name_to_rgb, rgb_to_hsv, rgb255_to_rgb
from scheduler_state import SchedulerState

from db.models import FappModel
from db.base import session_factory
from json import dumps

class Drawing(Fap):
    PLAYABLE = True
    ACTIVATED = True
    def __init__(self, username, userid):
        self.rate = Rate(10)
        Fap.__init__(self, username, userid)

    def handle_message(self, json_data, path=None): # noqa
        if json_data is None:
            raise ValueError("Error : message received on websocket is empty.")
        elif isinstance(json_data, str):
            data = loads(json_data)
        else:
            raise ValueError("Incorrect payload value type for Drawing Fapp")

        pixel = data['pixel']
        color = data['color']

        px_x = int(pixel['x'])
        px_y = int(pixel['y'])

        assert(isinstance(color['red'], int) and 0 <= color['red'] <= 255)
        assert(isinstance(color['green'], int) and 0 <= color['green'] <= 255)
        assert(isinstance(color['blue'], int) and 0 <= color['blue'] <= 255)

        self.model.set_pixel(px_x, px_y, rgb255_to_rgb(color['red'], color['green'], color['blue']))

    def set_default_drawing(self):
        # Set the current model as the default drawing in database
        session = session_factory()
        try:
            fap = session.query(FappModel).filter_by(name='Drawing').first()
            if not fap:
                return False
            fap.default_params = dumps({"model": self.model.json()})
            session.commit()
        finally:
            session.close()

    def run(self, params, expires_at=None):
        if 'model' in params and params['model'] != "":
            # Replay saved drawing
            self.model.set_from_json(params['model'])
            while True:
                self.send_model()
                self.rate.sleep()
        else:
            # Regular real-time drawing
            self.start_socket()
            while True:
                if SchedulerState.get_default_drawing_request():
                    self.set_default_drawing()
                self.send_model()
                self.rate.sleep()

