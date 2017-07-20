from aiohttp import web, WSMsgType
import aiohttp_mako
from mako.template import Template
import asyncio
from asyncio import async as asy
import discord
from threading import Thread
from voice_entry import VoiceEntry

bot = None
other_loop = None
websockets = {}

async def handle_main_page(request):
    text = "Hi!γ"
    return web.Response(text=text)

@aiohttp_mako.template("template.html")
async def handle_server(request):
    server_id = request.match_info.get('server_id', "")
    #other_loop.call_soon_threadsafe(asy ,
    #        bot.send_message(discord.Object(124790445598310400), "hi"))
    for server in bot.servers:
        if server.id == server_id:
            return {"server": server,
                    "voice": server.voice_client,
                    "player": server.voice_client.player if hasattr(server.voice_client, 'player') else None,
                    "current": server.voice_client.current if hasattr(server.voice_client, 'current') else None}
    #        response += server.name + "\n"
    #        for channel in server.channels:
    #            if channel.type != 'text':
    #                response += channel.name + "\n"
    #        return web.Response(text=response)
    #return web.Response(text=response+"not found")

async def riot_handler(request):
    with open('riot.txt') as f:
        return web.Response(text=f.readline())

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    ws_server_id = request.match_info.get("server_id", "")
    websockets[ws] = ws_server_id
    server = bot.servers_by_id[ws_server_id]
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            data = msg.data.split(' ')
            if msg.data == 'close':
                await ws.close()
            elif data[0] == "JOIN_CHANNEL":
                _, server_id, channel_id = data
                server = bot.servers_by_id[server_id]
                if server.voice_client != None:
                    for c in server.channels:
                        if c.id == channel_id:
                            other_loop.call_soon_threadsafe(asy,
                                    server.voice_client.move_to(c))
                            break
                else:
                    other_loop.call_soon_threadsafe(asy, bot.join_voice_channel(discord.Object(channel_id)))
                while server.voice_client == None:
                    await asyncio.sleep(1)
                bot.voice.append(server.voice_client)
                server.voice_client.player = None
                server.voice_client.queue = []
                for client in websockets:
                    if websockets[client] == ws_server_id:
                        client.send_str("JOINED_CHANNEL " + channel_id)
            elif data[0] == "MEDIA_PLAY":
                #TODO Actually play media
                if server.voice_client == None:
                    ws.send_str("LEFT_CHANNEL")
                    continue
                if server.voice_client.player.is_playing():
                    ws.send_str("MEDIA_PLAYING") #TODO send info about what is playig
                    continue
                if server.voice_client.player.is_done():
                    ws.send_str("MEDIA_OVER")
                    continue
                server.voice_client.player = server.voice_client.create_ffmpeg_player(
                        server.voice_client.current.url, before_options="-ss " + 
                        str(server.voice_client.current.position))
                server.voice_client.player.start()
                for client in websockets:
                    if websockets[client] == ws_server_id:
                        client.send_str("MEDIA_PLAYING");
            elif data[0] == "MEDIA_PAUSE":
                #TODO Actually pause media
                if server.voice_client == None:
                    ws.send_str("LEFT_CHANNEL")
                    continue
                if not server.voice_client.player.is_playing():
                    ws.send_str("MEDIA_PAUSED")
                    continue
                server.voice_client.player.pause()
                server.voice_client.current.position += server.voice_client.player.loops * \
                    server.voice_client.player.delay
                for client in websockets:
                    if websockets[client] == ws_server_id:
                        client.send_str("MEDIA_PAUSED");
            elif data[0] == "MEDIA_NEXT":
                if server.voice_client != None and server.voice_client.player != None and \
                        server.voice_client.player.is_playing():
                    server.voice_client.player.stop()
                    send_message(ws_server_id, "MEDIA_NEXT")
            elif data[0] == "MEDIA_PREVIOUS":
                if server.voice_client != None and server.voice_client.current != None:
                    server.voice_client.player = server.voice_client.create_ffmpeg_player(
                            server.voice_client.current.url)
                    server.voice_client.player.start()
                    send_message(ws_server_id, "MEDIA_PREVIOUS")
            elif data[0] == "MEDIA_QUEUE":
                d = msg.data.split('\n');
                audio_url, info = bot.get_url(d[1])
                #info = bot.ydl.extract_info(bot.yt.search_video(d[1]), download=False)
                entry = VoiceEntry(server, info["title"], audio_url, info["duration"], info["thumbnail"])
                if server.voice_client == None or hasattr(server.voice_client, "player") and server.voice_client.player == None \
                    or not (hasattr(server.voice_client, "player") and server.voice_client.player.is_playing()):
                    other_loop.call_soon_threadsafe(asy, bot.play_song(server.voice_client, entry))
                    send_message(ws_server_id, "MEDIA_QUEUED \n" +
                            str(entry.duration) + '\n' +
                            entry.title + '\n' +
                            entry.thumbnail_url)
                    send_message(ws_server_id, "MEDIA_NEXT")
                else:
                    if not hasattr(server.voice_client, "queue"):
                        server.voice_client.queue = []
                    server.voice_client.queue.append(entry)
                    send_message(ws_server_id, "MEDIA_QUEUED \n" +
                            str(entry.duration) + '\n' +
                            entry.title + '\n' +
                            entry.thumbnail_url)

            print(msg.data)
    websockets.pop(ws)
    return ws

def run():
    #_bot = bot
    second_loop = asyncio.new_event_loop()
    bot.otherloop = second_loop
    asyncio.set_event_loop(second_loop)
    app = web.Application()
    app.router.add_get('/', handle_main_page)
    app.router.add_get('/ws/{server_id}', websocket_handler)
    app.router.add_get('/riot.txt', riot_handler)
    app.router.add_get('/{server_id}', handle_server)
    app.router.add_static('/static', "static/")
    lookup = aiohttp_mako.setup(app, input_encoding='utf-8',
                                output_encoding='utf-8',
                                default_filters=['decode.utf8'])
    lookup.put_template("template.html", Template(filename="template.html"))
    web.run_app(app, port=8083)


def send_message(server_id, message):
    for ws in websockets:
        if websockets[ws] == server_id:
            ws.send_str(message)
