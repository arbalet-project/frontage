#!/usr/bin/env python

import asyncio
import websockets


class Toto:
    async def hello(self, websocket, path): # noqa
        while True:
            print("---")
            print(path)
            print("---")
            name = await websocket.recv()
            print("< {}".format(name))

            greeting = "Hello {}!".format(name)
            await websocket.send(greeting)
            print("> {}".format(greeting))


tt = Toto()
start_server = websockets.serve(tt.hello, '0.0.0.0', 8123)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
