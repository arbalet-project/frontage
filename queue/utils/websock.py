import asyncio
import websockets
import json
import logging

from utils.red import redis, redis_get
from threading import Thread

KEY_WS_SEND         = "KEY_WS_SEND"
KEY_USERS           = "KEY_USERS"
KEY_HASCHANGED      = "KEY_FRONTAGE_HAS_CHANGED"
KEY_GRANTUSER       = "KEY_GRANTED_USER"

class Websock(Thread):
    def __init__(self, fap, host='0.0.0.0', port=9988):
        Thread.__init__(self)
        self.fap = fap
        self.host = host
        self.port = port
        self.web_socket = None

    @staticmethod
    def get_users():
        users = redis_get(KEY_USERS, 'None')
        if (users == 'None'):
            return {'users': {'id': 'turnoff', 'username':'turnoff'}}
        return users

    @staticmethod
    def set_has_changed(bool=False, r=None, c=None, d=None):
        redis.set(KEY_HASCHANGED, json.dumps({'haschanged': bool,
                                              'rows': r,
                                              'cols': c,
                                              'disabled': d}))

    @staticmethod
    def set_grantUser(user): # user : { 'id': string, 'username': string}
        logging.info("Granting {}".format(user))
        redis.set(KEY_GRANTUSER, json.dumps({'id': user['id'],
                                             'username': user['username']}))

    @staticmethod
    def get_grantUser(): # user : { 'id': string, 'username': string}
        user = redis_get(KEY_GRANTUSER, 'None')
        if (user == 'None'):
            return None
        return user

    @staticmethod
    def send_data(code, message, username='', userid=''):
        redis.set(KEY_WS_SEND, json.dumps({'code': code,
                                           'message': message,
                                           'username': username,
                                           'userid': userid}))

    @staticmethod
    def get_data():
        data = redis_get(KEY_WS_SEND, None)
        if data:
            redis.set(KEY_WS_SEND, 'None')
        if data == 'None':
            return None
        return data

    async def consumer_handler(self, websocket, path): # noqa
        while True:
            data = await websocket.recv()
            self.fap.handle_message(data, path)

    async def producer_handler(self, websocket, path):
        while True:
            await asyncio.sleep(0.01)
            data_to_send = Websock.get_data()
            if data_to_send:
                await websocket.send(data_to_send)

    async def handler(self, websocket, path):
        consumer_task = asyncio.ensure_future(self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(self.producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.web_socket = websockets.serve(self.handler, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(self.web_socket)
        asyncio.get_event_loop().run_forever()

    def close(self):
        self.web_socket.ws_server.close()
