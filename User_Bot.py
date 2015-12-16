import logging
from os import system
from time import sleep

from Bot import Bot
from RiotAPI import log

"""
Rename this file with the name of your bot, or !restart won't work.
Additionally, you can set name, email and password to their values directly, instead of having to type them every time.
"""

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

name = input("Bot name: ")
email = input("Bot email: ")
password = input("Bot password: ")

user_bot = Bot(email, password, name)
system("cls")

user_bot.log(0)
system('title Botwyniel')

if not user_bot.is_logged_in:
    print("Logging in to Discord failed")
    exit(1)


@user_bot.event
def on_message(message):
    if message.content.startswith('!'):
        log(str(message.author) + ": " + message.content)
        if message.content.split(' ')[0] in user_bot.commands:
            user_bot.commands[message.content.split(" ")[0]](message)


@user_bot.event
def on_ready():
    log("Botwyniel initialized")
    user_bot.change_status(443)

    system("cls")
    print('Logged in as ' + user_bot.user.name)

    print("\nAvailable servers:")
    for a in user_bot.servers:
        print(a.name)
        user_bot.servs[a.name] = a
        ch_dict = {}
        for channel in a.channels:
            ch_dict[channel.name] = channel
        user_bot.channels[a] = ch_dict
    print('------')


@user_bot.event
def on_member_join(user):
    log(user.name + ' has joined ' + user.server.name)
    print(user.name + ' has joined ' + user.server.name)

sleep(0.5)
user_bot.run()
