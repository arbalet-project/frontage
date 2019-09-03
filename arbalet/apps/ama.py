#!/usr/bin/env python
"""
Presentation
"""

import time

from json import loads

from apps.fap import Fap
from apps.actions import Actions
from utils.tools import Rate
from utils.colors import name_to_rgb, rgb_to_hsv, rgb255_to_rgb
from utils.websock import Websock
from scheduler_state import SchedulerState

from db.models import FappModel
from db.base import session_factory
from json import dumps
from numpy import array

from time import sleep

from server.flaskutils import print_flush

class Ama(Fap) :
        PLAYABLE = True
        ACTIVATED = True
        #The F-app has three modes possible
        PARAMS_LIST = {'mode': ['ama', #AMA, or Assisted Manual Addressing, is the classic addressing procedure
                                'rac', #RAC, which is french for HAR, or Hot Assisted Readressing, is the addressing procedure performed to add pixels on the spot
                                'skip']} #Skip allow to retrieve the last addressing registered, and use it again.

        #Initialisation of the class
        def __init__(self, username, userid) :
                Fap.__init__(self, username, userid)
                self.action = 1 #Input regarding the validity of position
                self.rows = 0 #dimensions of the matrix
                self.cols = 0
                self.coord = (-1,-1)
                self.pixels = {}

        #Event handler function, calls every time a message is received from the Frontend
        def handle_message(self, json_data, path=None) :
            print_flush(json_data)
            #Retrieving and extracting the message
            if json_data is None :
                    raise ValueError("Error : empty message received from WebSocket")
            elif isinstance(json_data, str) :
                    data = loads(json_data)
            else :
                    raise ValueError("Incorrect payload value type for AMA Fapp")

            if (data.get('x') != None): #Coordinates were sent for the pixel
                    x = int(data['x'])
                    y = int(data['y'])
                    self.coord = (y, x) #Updating the pixel coordinate.
            elif (data.get('action') != None): #User specified validity of their input
                    self.action = data.get('action')
            else :
                    print_flush("Received unknown message from frontend")

        #Updates the Database : memorize the addressing of the pixels.
        def update_DB(self) :
            if self.pixels.get('default') : #Remove the fake pixel
                self.pixels.pop('default')
            #Update DB
            if (self.params['mode'] == 'ama' or self.params['mode'] == 'skip') : # in case of initial addressing, the previous configuration is first deleted.
                SchedulerState.drop_dic()
                print_flush("Database cleaned")
            while (len(self.pixels) != 0) : #Pixels are then added one by one to the database
                (mac, ((x,y),ind)) = self.pixels.popitem()
                SchedulerState.add_cell(x, y, mac, ind)
            print_flush("Database updated")
            rows = SchedulerState.get_rows()
            cols = SchedulerState.get_cols()
            disabled = SchedulerState.get_disabled()
            Websock.set_has_changed(True, rows, cols, disabled)

        #When addressing is over, but before admin close the F-app : makes App wait.
        def wait_to_be_kill(self):
            while True:
                print_flush("Addressing is over...")
                time.sleep(0.05)

        def run(self, params, expires_at=None) :
            self.params = params
            if (params['mode'] == 'skip'):
                self.wait_to_be_kill()
            self.start_socket()
            amount = 0
            # get necessary informations
            self.amount = SchedulerState.get_amount()
            self.rows = SchedulerState.get_rows()
            self.cols = SchedulerState.get_cols()
            # get the pixels to address
            while amount < self.amount :
                if (self.coord != (-1,-1)):
                    self.pixels[amount] = (self.coord, amount)
                    amount += 1
                    self.coord = (-1,-1)
            self.update_DB()
            self.wait_to_be_kill()
