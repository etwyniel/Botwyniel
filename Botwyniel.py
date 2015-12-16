import logging
from os import system
from time import sleep

from Bot import Bot
from RiotAPI import log

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

botwyniel = Bot('etwyspam@gmail.com', 'almg0308')
botwyniel.log(0)
system('title Botwyniel')

if not botwyniel.is_logged_in:
    print("Logging in to Discord failed")
    exit(1)


@botwyniel.event
def on_message(message):
    if message.content.startswith('!'):
        log(str(message.author) + ": " + message.content)
        if message.content.split(' ')[0] in botwyniel.commands:
            botwyniel.commands[message.content.split(" ")[0]](message)


@botwyniel.event
def on_ready():
    log("Botwyniel initialized")
    botwyniel.change_status(443)
    system("cls")
    print('Logged in as ' + botwyniel.user.name)

    print("\nAvailable servers:")
    for a in botwyniel.servers:
        print(a.name)
        botwyniel.servs[a.name] = a
        ch_dict = {}
        for channel in a.channels:
            ch_dict[channel.name] = channel
        botwyniel.channels[a] = ch_dict
    print('------')


@botwyniel.event
def on_member_join(user):
    log(user.name + ' has joined ' + user.server.name)
    print(user.name + ' has joined ' + user.server.name)

sleep(0.5)
botwyniel.run()
