import logging
from os import environ as en
from threading import Thread
from time import sleep

from Bot import Bot
from discord.game import Game
from TwitchAPI import check_for_stream

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

#bot created as a Bot object , taking an email address, a password
#and an optionnal whitelist of people allowed to use certain commands.
botwyniel = Bot(en["EMAIL"], en["PASSWORD"], wl=["Etwyniel", "Jhysodif"])
#bot attempts to connect, exits in case of failure
botwyniel.connect(0)

if not botwyniel.is_logged_in:
    print("Logging in to Discord failed")
    exit(1)


#bot waits for a message containing a command starting with "!", and executes the
#corresponding function.
@botwyniel.event
def on_message(message):
    if message.content.startswith('!'):
        if message.content.split(' ')[0] in botwyniel.commands:
            botwyniel.log(str(message.author) + ": " + message.content)
            botwyniel.commands[message.content.split(" ")[0]](message)


#Upon logging in, bot prints the names of the servers it is connected to in the console
@botwyniel.event
def on_ready():
    botwyniel.status(en["default_game"])
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
    botwyniel.log("Botwyniel initialized")

def check_twitch():
    live_now = []
    while True:
        streams = check_for_stream(en["twitch_account"])
        for stream in streams:
            if not stream[0] in live_now:
                live_now.append(stream[0])
                botwyniel.send_message(botwyniel.channels[botwyniel.servs["Etwyniel's"]]["twitch"],
                                       "{user} is live on twitch now, playing {game} !\n{title}\n{url}".format(
                                           user=stream[0],
                                           game=stream[1],
                                           title=stream[2],
                                           url=stream[3]))
        for streamer in live_now:
            if len(streams) == 0:
                live_now.remove(streamer)
                botwyniel.send_message(botwyniel.channels[botwyniel.servs["Etwyniel's"]]["twitch"],
                                       "{user}'s livestream is now over.".format(user=streamer))
            else:
                found = False
                for stream in streams:
                    if streamer in stream:
                        found = True
                if not found:
                    live_now.remove(streamer)
                    botwyniel.send_message(botwyniel.channels[botwyniel.servs["Etwyniel's"]]["twitch"],
                                           "{user}'s live is now over.".format(user=streamer))
        sleep(60)

twitch = Thread(target=check_twitch)
twitch.start()

#Main function of the bot.
botwyniel.run()
