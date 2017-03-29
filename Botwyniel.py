#!/usr/bin/python3

from Bot import Bot

try:
    keys = open(".keys")
    token = keys.readline()[:-1]
    keys.close()
    botwyniel = Bot(wl=["112836380245114880"])
    botwyniel.run(token)
except Exception as e:
    print(e)
    botwyniel = Bot(wl=["112836380245114880"])
    botwyniel.run(input("Token: "))
