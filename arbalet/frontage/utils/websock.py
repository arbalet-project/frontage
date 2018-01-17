import asyncio
import websockets

from utils.red import redis
from threading import Thread


class Websock(Thread):
    def __init__(self, fap, host='0.0.0.0', port=9988):
        self.fap = fap
        self.host = host
        self.port = port
        Thread.__init__(self)

    async def handle_client_message(self, websocket, path): # noqa
        while True:
            data = await websocket.recv()
            print('=====> GOT DATA' + data)
            self.fap.handle_message(data, path)

    def run(self):
        print('=====> Run Websock')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        web_socket = websockets.serve(self.handle_client_message, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(web_socket)
        asyncio.get_event_loop().run_forever()
        print('=====> Close Websock')
