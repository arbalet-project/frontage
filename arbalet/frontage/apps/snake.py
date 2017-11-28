
import asyncio
import websockets

from apps.fap import Fap
from utils.colors import name_to_rgb


async def hello(websocket, path):  # noqa
    name = await websocket.recv()
    print("< {}".format(name))

    greeting = "Hello {}!".format(name)
    await websocket.send(greeting)
    print("> {}".format(greeting))


class Snake(Fap):

    PLAYABLE = False
    ACTIVATED = True

    PARAMS_LIST = {}

    def run(self, params):
        start_server = websockets.serve(hello, '0.0.0.0', 8124)
        print('====> Start SNAKE')
        while True:
            print('====> Run')
            asyncio.get_event_loop().run_until_complete(start_server)
            print('====> Run 2')
            asyncio.get_event_loop().run_forever()
            print('====> Run 3')
