#!/usr/bin/env python
"""
    Arbalet Frontage

    Copyright 2015 Yoan Mollard - Arbalet project - http://github.com/arbalet-project
    License: GPL version 3 http://www.gnu.org/licenses/gpl.html
"""
import pika
import logging
from os import environ
import sys
from json import dumps, loads
from threading import RLock
from apps.fap import Fap
from scheduler_state import SchedulerState
from utils.security import authentication_required, is_admin
from utils.websock import Websock

class Snap(Fap):
    PLAYABLE = True
    OFF = {'id':"turnoff", 'username':"turnoff"}

    def __init__(self, username, userid):
        Fap.__init__(self, username, userid)
        self.user = Snap.OFF
        self.users = []
        self.lock = RLock()
        self.channelserver = None
        self.consumme = 0
        self.connectionserver = None
        credentials = pika.PlainCredentials(environ['RABBITMQ_DEFAULT_USER'], environ['RABBITMQ_DEFAULT_PASS'])
        self.paramsserver = pika.ConnectionParameters(host='rabbit', credentials=credentials, connection_attempts = 100, heartbeat = 60)

    @staticmethod
    def scale(v):
        return min(1., max(0., float(v)/255))

    def callback(self, ch, method, properties, body):
        self.consumme += 1
        listpixels = loads(body.decode('ascii'))
        nuser = loads(Websock.get_grantUser())
        if(nuser.get('id') is None or nuser.get('id') == "turnoff"):
            logging.info("Turn off request")
            self.erase_all()
        elif nuser['id'] != self.user['id']:
            self.user = nuser
            self.erase_all()
            self.set_rgb_matrix(listpixels['pixels'])
        else:
            self.set_rgb_matrix(listpixels['pixels'])

    def set_rgb_matrix(self, listpixels):
        nb_rows = SchedulerState.get_rows()
        nb_cols = SchedulerState.get_cols()
        r = 0
        c = 0
        with self.lock:
            for pix in listpixels:
                r = pix.get('rowX')
                c = pix.get('columnY')
                try:
                    hexacolor = int(pix.get('color')[1:], 16)
                    red = (hexacolor & 0xFF0000) >> 16
                    green = (hexacolor & 0x00FF00) >> 8
                    blue = (hexacolor & 0x0000FF)
                    self.model.set_pixel(r, c, list(map(Snap.scale, [red, green, blue])))
                except:
                    logging.error("ERRROR : invalid pixel {}".format(pix))
            self.send_model()
            return 'OK'

    def erase_all(self):
        with self.lock:
            self.model.set_all((0,0,0))
            self.send_model()
        return 'OK'

    def run(self, params, expires_at=None):
        with self.lock:
            self.model.set_all((0,0,0))
            self.send_model()
        users = loads(Websock.get_users())['users']
        if (len(users) == 1):
            self.user = users[0]
        Websock.set_grantUser(self.user)
        self.connectionserver = pika.BlockingConnection(self.paramsserver)
        self.channelserver = self.connectionserver.channel()

        self.channelserver.exchange_declare(exchange='logs', exchange_type='fanout')

        result = self.channelserver.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        self.channelserver.queue_bind(exchange='logs', queue=queue_name)
        self.channelserver.basic_consume(queue=queue_name, on_message_callback=self.callback, auto_ack=True)

        logging.info('Waiting for pixel data on queue "{}".'.format(queue_name))
        self.channelserver.start_consuming()
