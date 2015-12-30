import logging
from os import environ as en

from Bot import Bot

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
        botwyniel.log(str(message.author) + ": " + message.content)
        if message.content.split(' ')[0] in botwyniel.commands:
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


#Main function of the bot.
botwyniel.run()
