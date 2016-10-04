import threading
from datetime import datetime, date
from threading import Thread
from random import randrange
import asyncio
import subprocess
import os
from ctypes.util import find_library
import requests
import pymysql

import discord
from RiotAPI import RiotAPI
from YoutubeAPI import YoutubeAPI
from discord.client import ConnectionState


class VoiceEntry:
    def __init__(self, message, song):
        self.requester = message.author
        self.channel = message.channel
        self.song = song

class Bot(discord.Client):
    """
    Bot object that inherits from the Client object of discord.py
    Mostly designed for League of Legends.
    """
    
    def __init__(self, name="Botwyniel", wl=[], **kwargs):
        super().__init__()
        self.player = None
        self.init_time = datetime.now()
        self.servs = {}
        self.channels = {}
        self.aliases = {}
        self.yt = YoutubeAPI()
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.name = name
        self.whitelist = wl
        self.steam_key = "7079BC4D125AF8E3C3D362F8A98235CC"
        self.riot_key = "88e79b8e-39c5-45f6-b2c5-c5606e6f37c5"
        self.regions = ["BR", "EUNE", "EUW", "KR", "LAN", "LAS", "NA", "OCE", "TR", "RU", "JP", "PBE"]
        self.commands = {"0!rank": self.rank,
                         "0!gameranks": self.gameranks,
                         "0!uptime": self.send_uptime,
                         "0!status": self.status,
                         "0!send": self.send,
                         "0!fc": self.free_champs,
                         "0!py": self.execute,
                         "0!help": self.help,
                         "0!ytlatest": self.latest_videos,
                         "0!ytsearch": self.search_video,
                         "0!ytthumbnail": self.get_thumbnail,
                         "0!avatar": self.avatar,
                         "0!sendpm": self.sendpm,
                         "0!love": self.love,
                         "0!8ball": self.eightball,
                         "0!dice": self.dice,
                         "0!coin": self.coin,
                         "0!suggest": self.suggest,
                         "0!play": self.play_song,
                         "0!pause": self.pause,
                         "0!ytplay": None,
                         "0!setalias": self.set_alias,
                         "0!removealias": self.remove_alias,
                         "0!about": self.about
                         }
        self.commands_help = {"0!rank": "Returns the rank of the specified player. If your Discord username is the "
                                  "same as your summoner name, or if you have set an alias using 0!setalias, you can use 0!rank me, *region* or 0!rank instead.\n"
                                  "Syntax: `0!rank username (, region)`    -- region is optional if the player you are looking is on EUW",
                              "0!gameranks": "Returns the ranks of the players in the game the specified player is "
                                  "currently in. If your Discord username is the same as your summoner "
                                  "name, or if you have set an alias using 0!setalias, you can use !gameranks me, *region* or 0!gameranks instead.\n"
                                  "Syntax: `0!gameranks username (, region)`     -- region if the player you are looking for is on EUW",
                              "0!uptime": "Returns the duration for which the bot has been running.",
                              "0!status": "Changes the game the bot is playing to the specified game.",
                              "0!send": "Makes the bot send a message to the specified channel. The bot needs to be "
                                  "connected to this server for this command to function.",
                              "0!love": "Send Botwyniel some love!",
                              "0!fc": "Returns this week's free champions.",
                              "0!py": "Executes a python command or block of code. Admin-only.",
                              "0!help": "...really?",
                              "0!ytsearch": "Sends the URL of the first corresponding youtube video.",
                              "0!ytlatest": "Sends the URL of the last 3 videos of the specified youtube channel.",
                              "0!ytthumbnail": "Sends the thumbnail of the first corresponding youtube video.",
                              "0!avatar": "Sends the URL of the mentionned user's avatar.\n"
                                  "Syntax: `0!avatar @username`",
                              "0!sendpm": "Sends a private message to the mentionned user.",
                              "0!8ball": "Ask me a question!",
                              "0!coin": "Flip a coin!",
                              "0!dice": "Roll n dices with x faces.\n The command should look like this: **ndx**",
                              "0!suggest": "Make a suggestion to improve " + self.name,
                              "0!setalias": "Tell Botwyniel to remember your LoL username and region, so you can call 0!rank and 0!gameranks without arguments.\n"
                                  "Syntax: `0!setalias username, region`",
                              "0!removealias": "Tell Botwyniel to forget your alias.\n"
                                  "Syntax: `0!removealias`"
                              }
    async def on_ready(self):
        print('Logged in as ' + self.user.name)
        self.fetch_aliases()
        self.loop.create_task(self.check_update())
        
        self.list_servers()
        await self.log("Botwyniel initialized")
        chans = self.servs["Etwyniel's"].channels
        if not discord.opus.is_loaded():
            pass
			#discord.opus.load_opus('vendor/lib/libopus.so.0')
                #await self.log('Failed to load opus: ' str(e))
        """
		for c in chans:
            if str(c.type) != 'text' and c.name == 'Music':
                self.voice = await self.join_voice_channel(c)
		"""

    async def on_message(self, message):
##        if message.content == '0!play':
##            url = 'https://www.youtube.com/watch?v=B1O0R0t6zdI'
##            subprocess.call('youtube-dl --metadata-from-title "%(artist)s - %(title)s"\
##--extract-audio --audio-format mp3 --add-metadata ' + url)
##            video_id = url[url.find('=')+1:]
##            for f in os.listdir('.'):
##                if video_id in f:
##                    filename = f
##                    break
##            await self.songs.put(VoiceEntry(message, filename))
##            self.current = await self.songs.get()
##            self.player = self.voice.create_ffmpeg_player(self.current.song, after=self.delete_file)
##            self.player.start()
        if message.content.startswith('0!play'):
            await self.play_song(message)
        elif message.content.startswith('0!'):
            if message.content.split(' ')[0] in self.commands:
                await self.log(str(message.author) + ": " + message.content)
                await self.commands[message.content.split(" ")[0]](message)

    async def pause(self, message):
        if self.player != None and self.player.is_playing():
            self.player.pause()
        else:
            pass

    async def play_song(self, message):
        if self.player != None and self.player.is_playing():
            await self.send_message(message.channel, 'Already playing.')
            return None
        await self.send_typing(message.channel)
        query = message.content[message.content.find(' ')+1:]
        url = self.yt.search_video(query)
        self.player = await self.voice.create_ytdl_player(url)
        self.player.start()
        await self.send_message(message.channel, 'Now playing `' + self.player.title + '`')

    def list_servers(self):
        print("\nLogged in to {} servers.".format(len(self.servers)))
        for a in self.servers:
            #print(a.name)
            self.servs[a.name] = a
            ch_dict = {}
            for channel in a.channels:
                ch_dict[channel.name] = channel
            self.channels[a] = ch_dict
        print('------')
        
    def fetch_aliases(self):
        conn = self.db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM aliases")
        row = cursor.fetchone()
        while row != None:
            self.aliases[row[0]] = [row[1], row[2]]
            row = cursor.fetchone()

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

    async def send_uptime(self, message):
        await self.send_typing(message.channel)
        await self.send_message(message.channel, self.uptime(message))

    async def love(self, message):
        outputs = ["You smart. You loyal. You’re grateful. I appreciate that."
                        "Go buy your momma a house. Go buy your whole family houses."
                        "Put this money in your savings account. Go spend some money for no reason."
                        "Come back and ask for more.",
                   "Marry me!",
                   "No. F*ck you.",
                   "*Faints in a puddle of tears of happiness*",
                   "You're just one of many.",
                   "Don't tell the others, but I love you too.",
                   "This needs to stop.",
                   "You da real MVP!",
                   "Alright, I won't kill you.",
                   "Ok, I'll kill you last.",
                   "Umm... wrong number.",
                   "Love received!"]
        await self.send_message(message.author, outputs[randrange(len(outputs))])

    async def status(self, message):
        if type(message) == discord.Message:
            message.content = self.truncate(message.content)
            game = discord.Game(name=message.content)
            self.change_status(game)
            self.current_status = message.content
        else:
            game = discord.Game(name=message)
            self.change_status(game)
            self.current_status = message

    async def avatar(self, message):
        if len(message.mentions) == 0:
            await self.send_message(message.channel, message.author.avatar_url)
        else:
            try:
                for user in message.mentions:
                    await self.send_message(message.channel, user.avatar_url)
            except discord.errors.HTTPException:
                await self.send_message(message.channel, "This user does not have an avatar.")

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
        return username, region.lower()

    def author_is_admin(self, message):
        return message.author.name in self.whitelist

    async def rank(self, message):
        await self.send_typing(message.channel)
        player = self.get_player(message)
        username = player[0]
        region = player[1]

        if region.upper() not in self.regions:
            await self.send_message(message.channel, 'Invalid region')
            return None
        
        if username in ["me", '']:
            if message.author.id in self.aliases:
                username, region = self.aliases[message.author.id]
            else:
                username = message.author.name
        try:
            riot = RiotAPI(self.riot_key, region)
            rank = riot.get_summoner_rank("".join(username.split(" ")))

            to_return = "The summoner {username} is ranked {tier} {division} and currently has {LP} LPs. (S6 winrate: {winrate}%)".format(
                username=username,
                tier=rank[0].capitalize(),
                division=rank[1],
                LP=str(rank[2]),
                winrate=str(rank[3])
            )

        except (ValueError, KeyError):
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
        await self.send_message(message.channel, to_return)

    async def gameranks(self, message):
        await self.send_typing(message.channel)
        
        player = self.get_player(message)
        username = player[0]
        region = player[1]

        if region.upper() not in self.regions:
            await self.send_message(message.channel, 'Invalid region')
            return None

        if username in ["me", '']:
            if message.author.id in self.aliases:
                username, region = self.aliases[message.author.id]
            else:
                username = message.author.name

        riot = RiotAPI(self.riot_key, region)
        ranks = riot.get_game_ranks("".join(username.split(" ")))

        if not ranks:
            await self.send_message(message.channel, "The summoner {username} is "
             "not currently in a game or does not exist.".format(
                username=username
            )
                              )
            return None
        
        to_send = "**Red team**:\n"
        for player in ranks:
            if ranks.index(player) == len(ranks)/2:
                to_send += "\n**Blue team**:\n"
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
        await self.send_message(message.channel, to_send)

    async def latest_videos(self, message):
        username = self.truncate(message.content)
        try:
            await self.send_message(message.channel, self.yt.latest_vids(username))
        except IndexError:
            await self.send_message(message.channel, "The {} channel does not seem to exist.".format(username))

    async def search_video(self, message):
        query = self.truncate(message.content)
        try:
            await self.send_message(message.channel, self.yt.search_video(query))
        except IndexError:
            await self.send_message(message.channel, "No video found matching this query.")

    async def get_thumbnail(self, message):
        query = self.truncate(message.content)
        try:
            await self.send_message(message.channel, self.yt.get_thumbnail(query))
        except IndexError:
            await self.send_message(message.channel, "No video found matching this query.")

    async def dice(self, message):
        try:
            arguments = self.truncate(message.content)
            n = int(arguments.split('d')[0])
            d = int(arguments.split('d')[1])
            if n > 10:
                to_return = 'Too many dices!'
            elif d > 100:
                to_return = 'Too many faces!'
            else:
                to_return = ''
                sum = 0
                for a in range(n-1):
                    number = randrange(d) + 1
                    sum += number
                    to_return += str(number) + ' + '
                number = randrange(d) + 1
                sum += number
                to_return += str(number) + ' = ' + str(sum)
        except:
            to_return = 'Invalid format!'
        await self.send_message(message.channel, to_return)

    async def coin(self, message):
        value = randrange(2)
        if value:
            to_return = 'Heads!'
        else:
            to_return = 'Tails!'
        await self.send_message(message.channel, to_return)

    async def send(self, message):
        args = self.truncate(message.content).split(", ")
        server = args[0]
        channel = args[1]
        message.content = ", ".join(args[2:])
        chan = self.channels[self.servs[server]][channel]
        await self.send_typing(chan)
        await self.send_message(chan, message.content)

    async def sendpm(self, message):
        m = self.truncate(message.content)
	receiver = message.mentions[0]
        if not message.channel.is_private and receiver.nick != None
            m = m.replace("@" + receiver.nick + " ", "")
        else:
            m = m.replace("@" + receiver.name + " ", "")
        await self.send_message(receiver, m)

    def kill(self, message):
        if self.author_is_admin(message):
            self.send_message(message.channel,
                              "TRAITOR! ({uptime})".format(user=message.author.name,
                                                                                 uptime=self.uptime(message)))
            exit(1)
        else:
            self.send_message(message.channel, "This is an admin-only command")

    async def free_champs(self, message):
        await self.send_typing(message.channel)
        riot = RiotAPI(self.riot_key)
        free_champs = riot.get_free_champions()
        to_send = "The free champions this week are {champions} and {last}.".format(
            champions=", ".join(free_champs[0:len(free_champs) - 1]),
            last=free_champs[len(free_champs) - 1]
        )
        await self.send_message(message.channel, to_send)

    async def eightball(self, message):
        """THERE YOU GO VANERI!"""
        outputs = ["Hell no.",
                   "Absolutely not!",
                   "I don't think so.",
                   "Outlook not so good.",
                   "Don't count on it.",
                   "My sources say no.",
                   "Very doubtful.",
                   "My reply is no.",
                   "You won't like the answer...",
                   "Forget about it.",
                   "I have my doubts.",
                   "Are you kidding?",
                   "Don't bet on it.",
                   "Forget about it.",
                   "It is certain.",
                   "It is decidedly so.",
                   "As I see it, yes.",
                   " You may rely on it.",
                   "Without a doubt.",
                   "Outlook good.",
                   "Concentrate and ask again.",
                   "Reply hazy try again.",
                   "Cannot predict now.",
                   "Yes.",
                   "No.",
                   "Better not tell you now.",
                   "Ask again later.",
                   "Cannot predict now.",
                   "As I see it, yes."]
        to_send = outputs[randrange(len(outputs))]
        await self.send_message(message.channel, to_send)
        await self.log("Answer: " + to_send)

    async def execute(self, message):
        if not self.author_is_admin(message):
            await self.send_message(message.channel, "This is an admin-only command.")
            return None
        try:
            command = ""
            for char in self.truncate(message.content):
                if char == '\n':
                    if command.startswith('await'):
                        await eval(command.split('await ')[1])
                    else:
                        exec(command)
                    command = ""
                else:
                    command += char
            if command.startswith('await'):
                await eval(command.split('await ')[1])
            else:
                exec(command)
        except Exception as e:
            await self.log(str(e))
            await self.send_message(message.channel, "Error occured: " + str(e))
            
    async def suggest(self, message):
        suggestion = self.truncate(message.content)
        if suggestion != "":
            await self.send_message(self.channels[self.servs['Etwyniel\'s']]['suggestions'], message.author.id + ': ' + suggestion)
            await self.send_message(message.channel, "Thanks for the suggestion!")
        else:
            await self.send_message(message.channel, "Please enter a suggestion.")

    async def help(self, message):
        if self.truncate(message.content) == "":
            await self.send_message(message.author, "The available commands are:\n"
            "**0!rank** *username*, *region*\*\n"
            "**0!gameranks** *username*, *region*\*\n"
            "**0!setalias** *username*, *region*\*\n"
            "**0!removealias**\n"
            "**0!avatar** @*user*\n"
            "**0!ytsearch** *query*\n"
            "**0!ytlatest** *channel name*\n"
            "**0!ytthumbnail** *query*\n"
            "**0!uptime**\n"
            "**0!send** *server*, *channel*, message\n"
            "**0!sendpm** @*user* *message*\n"
            "**0!fc**\n"
            "**0!love**\n"
            "**0!8ball** *question*\n"
            "**0!coin**\n"
            "**0!dice** *number of dices* d *type of dice*\n"
            "**0!status** *game id*\n"
            "**0!suggest** *suggestion*\n"
            "**0!about**\n"
            "**optional, default is euw.*\n\n"
            "Please type '0!help *command*' for more precise instructions.")
        elif self.truncate(message.content) in self.commands:
            await self.send_message(message.author, self.commands_help[self.truncate(message.content)])
        else:
            await self.send_message(message.author, "Unknown command.")
            
    async def about(self, message):
        self.send_message(message.channel, ("I am a discord bot created by Etwyniel, using discord.py by Rapptz.\n"
            "I can find your League of Legends rank, or the ranks of the people you are playing with and against.\n"
            "I can also find videos on YouTube.\n\n"
            "I am currently used by {} servers.").format(str(len(self.servers))))

    async def log(self, event):
        channel = self.channels[self.servs["Etwyniel's"]]["logs"]
        to_send = "[{date}] - *{time}*\n{event}".format(
            date=str(date.today()),
            time="".join(str(datetime.now().time()).split(".")[0])[0:5],
            event=event)
        await self.send_message(channel, to_send)
		
    async def set_alias(self, message):
        id = message.author.id
        m = self.truncate(message.content)
        if ',' in m:
            alias, region = m.split(', ')
        else:
            alias = m
            region = 'euw'
        if len(alias) > 32:
            self.send_message(message.channel, "This alias is too long.")
        elif alias == "":
            self.send_message(message.channel, "Please enter your alias.")
        elif region.upper() not in self.regions:
            self.send_message(message.channel, "Please enter a valid region.")
            
        conn = self.db_connect()
        cursor = conn.cursor()
        if id in self.aliases:
            query = "UPDATE aliases SET alias = '{1}', region = '{2}' WHERE id = '{0}';"
        else:
            query = "INSERT INTO aliases (id, alias, region) VALUES ('{0}', '{1}', '{2}');"
        cursor.execute(query.format(id, alias, region))
        conn.commit()
        conn.close()
        self.aliases[id] = [alias, region]
        await self.send_message(message.channel, "Alias {} successfully set!".format(alias))
        
    async def remove_alias(self, message):
        conn = self.db_connect()
        cursor = conn.cursor()
        id = message.author.id
        cursor.execute("SELECT alias FROM aliases WHERE id = '{}'".format(id))
        alias = cursor.fetchone()[0]
        query = "DELETE FROM aliases WHERE id = '{}'"
        cursor.execute(query.format(id))
        conn.commit()
        conn.close()
        self.aliases.pop(id)
        await self.send_message(message.channel, "Alias {} successfully removed!".format(alias))
            
    def db_connect(self):
        db = os.environ['CLEARDB_DATABASE_URL'][8:]
        db_server = db[db.index('@') + 1:db.index('/')]
        db_username = db[:db.index(':')]
        db_password = db[db.index(':') + 1:db.index('@')]
        db_database = db[db.index('/') + 1:db.index('?')]
        
        conn = pymysql.connect(host=db_server, user=db_username, password=db_password, db=db_database)
        return conn

    async def check_update(self):
        # What a mess...
        league_url = "http://euw.leagueoflegends.com/en/news/"
        
        
        #current_version = requests.get(db_url, params=args).text
        while True:
            channel = discord.Object('211180551502168064')
            
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM botwyniel_data WHERE name='last update'")
            current_version = cursor.fetchone()[1]
            #current_version = requests.get(db_url, params=args).text
            
            patch_page = requests.get(league_url).text
            index = patch_page.index("lol-core-file-formatter")
            field = patch_page[patch_page.rfind("<", 0, index):patch_page[index:].find(">") + index]
            latest_version = field[field.index("title=") + 7:field[field.index("title=") + 7:].index('"') + field.index("title=") + 7]
            
            if current_version != latest_version:
                patch_url = "http://euw.leagueoflegends.com" + \
                    field[field.index("href=") + 6:field[field.index("href=") + 6:].index('"') + field.index("href=") + 6]
                await self.send_message(channel, "New League of Legends update!\n" + patch_url)
                cursor.execute("UPDATE botwyniel_data SET val='{}' WHERE name='last update'".format(latest_version))
                conn.commit()
                current_version = latest_version
            conn.close()
            await asyncio.sleep(900)
        

if not discord.opus.is_loaded():
    pass
    #discord.opus.load_opus('libopus/build/lib/libopus.so.0.5.0')
    
botwyniel = Bot(wl=["Etwyniel", "Jhysodif"])
botwyniel.run(os.environ['DISCORD_TOKEN'])
