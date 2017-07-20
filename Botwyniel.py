#!/usr/bin/python3

from Bot import Bot
import asynchttpserver
from threading import Thread
import asyncio

try:
    keys = open(".keys")
    token = keys.readline()[:-1]
    keys.close()
    botwyniel = Bot(wl=["112836380245114880"])
    asynchttpserver.bot = botwyniel
    asynchttpserver.other_loop = asyncio.get_event_loop()
    thread = Thread(target=asynchttpserver.run)
    thread.start()
    botwyniel.run(token)
except Exception as e:
    print(e)
    botwyniel = Bot(wl=["112836380245114880"])
    botwyniel.run(input("Token: "))
