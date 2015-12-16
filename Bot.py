import threading
from datetime import datetime
from os import system, chdir
from time import sleep

import discord
from RiotAPI import RiotAPI, log
from discord.client import ConnectionState


class Bot(discord.Client):
    def __init__(self, username, password, name="Botwyniel", **kwargs):
        self.init_time = datetime.now()
        self._is_logged_in = False
        self._close = False
        self.options = kwargs
        self.connection = ConnectionState(self.dispatch, **kwargs)
        self.dispatch_lock = threading.RLock()
        self.token = ''
        self.servs = {}
        self.channels = {}
        self.name = name

        # the actual headers for the request...
        # we only override 'authorization' since the rest could use the defaults.
        self.headers = {
            'authorization': self.token,
        }
        self.username = username
        self.password = password
        self.riot_key = "88e79b8e-39c5-45f6-b2c5-c5606e6f37c5"
        self.regions = ["BR", "EUNE", "EUW", "KR", "LAN", "LAS", "NA", "OCE", "TR", "RU", "PBE"]
        self.commands = {"!rank": self.rank,
                         "!gameranks": self.gameranks,
                         "!uptime": self.send_uptime,
                         "!status": self.status,
                         "!send": self.send,
                         "!kill": self.kill,
                         "!fc": self.free_champs,
                         "!py": self.execute,
                         "!help": self.help,
                         "!join": self.join_server,
                         "!restart": self.restart
                         }
        self.commands_help = {"!rank": "Returns the rank of the specified player. If your Discord username is the "
                                       "same as your summoner name, you can use !rank me, *region* instead.",
                              "!gameranks": "Returns the ranks of the players in the game the specified player is "
                                            "currently in. If your Discord username is the same as your summoner "
                                            "name, you can use !gameranks me, *region* instead.",
                              "!uptime": "Returns the duration for which the bot has been running.",
                              "!status": "Changes the game the bot is playing to the specified game.",
                              "!send": "Makes the bot send a message to the specified channel. The bot needs to be "
                                       "connected to this server for this command to function.",
                              "!kill": "Stops the bot. Admin-only.",
                              "!fc": "Returns this week's free champions.",
                              "!py": "Executes a python command or block of code. Admin-only.",
                              "!help": "...really?",
                              "!join": "Makes the bot accept an instant invite (http://discord.gg/xxxxxxxx)."
                              }

    def uptime(self, ignore):
        uptime = datetime.now() - self.init_time
        uptime = str(uptime).split(".")[0].split(":")
        if uptime[0] == "0":
            to_return = "I have been running for {m}m and {s}s.".format(m=uptime[1], s=uptime[2])
            if uptime[1] == "00":
                to_return = "I have been running for {s}s.".format(s=uptime[2])
        else:
            to_return = "I have been running for {h}h{m}m and {s}s.".format(h=uptime[0], m=uptime[1], s=uptime[2])
        return to_return

    def send_uptime(self, message):
        self.send_typing(message.channel)
        self.send_message(message.channel, self.uptime(message))

    def log(self, ignore):
        print("Logging in...")
        self.login(self.username, self.password)
        if not self.is_logged_in:
            print("Logging in to Discord failed")
            exit(1)

    def status(self, message):
        message = self.truncate(message.content)
        self.change_status(int(message))

    @staticmethod
    def truncate(message):
        message = " ".join(message.split(" ")[1:])
        if "```" in message:
            message = message.split('```')[1]
        return message

    def get_player(self, message):
        m = self.truncate(message.content)
        m = m.split(', ')
        username = m[0]
        try:
            region = m[1]
        except IndexError:
            region = 'euw'
        return username, region

    @staticmethod
    def author_is_admin(message):
        roles = []
        for r in message.author.roles:
            roles.append(r.name)
        return "admin" in roles

    def join_server(self, message):
        url = self.truncate(message.content)
        self.accept_invite(url)

    def rank(self, message):
        self.send_typing(message.channel)
        player = self.get_player(message)
        username = player[0]
        region = player[1]

        if region.upper() not in self.regions:
            self.send_message(message.channel, 'Invalid region')
            return None
        riot = RiotAPI(self.riot_key, region)
        if username == "me":
            username = message.author.name
        try:
            rank = riot.get_summoner_rank("".join(username.split(" ")))

            to_return = "The summoner {username} is ranked {tier} {division} and currently has {LP} LPs.".format(
                username=username,
                tier=rank[0].capitalize(),
                division=rank[1],
                LP=str(rank[2])
            )

        except ValueError:
            try:
                level = riot.get_summoner_level("".join(username.split(" ")))
                to_return = "The summoner {username} is unranked and is level {level}.".format(
                    username=username,
                    level=str(level)
                )

            except:
                to_return = "The summoner {username} does not exist or is not on the {region} server.".format(
                    username=username,
                    region=region
                )
        self.send_message(message.channel, to_return)

    def gameranks(self, message):
        self.send_typing(message.channel)
        player = self.get_player(message)
        username = player[0]
        region = player[1]

        if region.upper() not in self.regions:
            self.send_message(message.channel, 'Invalid region')
            return None

        if username == "me":
            username = message.author.name

        riot = RiotAPI(self.riot_key, region)
        ranks = riot.get_game_ranks("".join(username.split(" ")))

        if not ranks:
            self.send_message(message.channel, "The summoner {username} is "
             "not currently in a game or does not exist.".format(
                username=username
            )
                              )
            return None

        to_send = "**Blue team**:\n"
        for player in ranks:
            if ranks.index(player) == 5:
                to_send += "\n**Red team**:\n"
            if player[2] == "unranked":
                to_send += "{name} (**{champion}**): Unranked\n".format(
                    name=player[0],
                    champion=player[1]
                )
            else:
                to_send += "{name} (**{champion}**): {tier} {division}\n".format(
                    name=player[0],
                    champion=player[1],
                    tier=player[2].capitalize(),
                    division=player[3]
                )
        self.send_message(message.channel, to_send)

    def send(self, message):
        args = self.truncate(message.content).split(", ")
        server = args[0]
        channel = args[1]
        message.content = ", ".join(args[2:])
        chan = self.channels[self.servs[server]][channel]
        self.send_typing(chan)
        self.send_message(chan, message.content)

    def kill(self, message):
        if message.author.name == "Jhysodif":
            self.send_message(message.channel,
                              "Y u do dis {user} :astonished: ({uptime})".format(user=message.author.name,
                                                                                 uptime=self.uptime(message)))
            self.logout()
            sleep(5)
            self.log(0)
            self.send_message(message.author, "Screw you!")
        elif self.author_is_admin(message) and message.server.name == "Etwyniel's":
            self.send_message(message.channel,
                              "Y u do dis {user} :astonished: ({uptime})".format(user=message.author.name,
                                                                                 uptime=self.uptime(message)))
            exit(1)
        else:
            self.send_message(message.channel, "This is an admin-only command")

    def free_champs(self, message):
        self.send_typing(message.channel)
        riot = RiotAPI(self.riot_key)
        free_champs = riot.get_free_champions()
        to_send = "The free champions this week are {champions} and {last}.".format(
            champions=", ".join(free_champs[0:len(free_champs) - 1]),
            last=free_champs[len(free_champs) - 1]
        )
        self.send_message(message.channel, to_send)

    def execute(self, message):
        if not self.author_is_admin(message):
            self.send_message(message.channel, "This is an admin-only command.")
            return None
        try:
            exec(self.truncate(message.content))
        except Exception as e:
            log(str(e))
            self.send_message(message.channel, "Error occured: " + str(e))

    def help(self, message):
        if self.truncate(message.content) == "":
            self.send_message(message.author, "The available commands are:\n\
            **!rank** *username*, *region*\*\n\
            **!gameranks** *username*, *region*\*\n\
            **!uptime**\n\
            **!send** *server*, *channel*, message\n\
            **!fc**\n\
            **!status** *game id*\n\
            **!kill** (admin only)\n\
            **!py** *command* (admin only)\n\
            **optional, default is euw.*\n\n\
            Please type '!help *command*' for further instructions.")
        elif self.truncate(message.content) in self.commands:
            self.send_message(message.author, self.commands_help[self.truncate(message.content)])
        else:
            self.send_message(message.author, "Unknown command.")

    def restart(self, message):
        if self.author_is_admin(message) and message.server.name == "Etwyniel's":
            chdir('..')
            system("call start {}.py".format(self.name))
            exit(1)
