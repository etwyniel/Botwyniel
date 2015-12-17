import logging

from Bot import Bot

# Set up the logging module to output diagnostic to the console.
logging.basicConfig()

botwyniel = Bot('etwyspam@gmail.com', 'almg0308')
botwyniel.connect(0)

if not botwyniel.is_logged_in:
    print("Logging in to Discord failed")
    exit(1)


@botwyniel.event
def on_message(message):
    if message.content.startswith('!'):
        botwyniel.log(str(message.author) + ": " + message.content)
        if message.content.split(' ')[0] in botwyniel.commands:
            botwyniel.commands[message.content.split(" ")[0]](message)


@botwyniel.event
def on_ready():
    botwyniel.change_status(443)
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


@botwyniel.event
def on_member_join(user):
    botwyniel.log(user.name + ' has joined ' + user.server.name)
    print(user.name + ' has joined ' + user.server.name)

botwyniel.run()
