#!/usr/bin/env python

import asyncio
import websockets

async def hello():
    async with websockets.connect('ws://192.168.1.23:8124') as websocket:
        name = input("What's your name? ")
        await websocket.send(name)
        print("> {}".format(name))

        greeting = await websocket.recv()
        print("< {}".format(greeting))

asyncio.get_event_loop().run_until_complete(hello())