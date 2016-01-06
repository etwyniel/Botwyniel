import requests
from time import sleep
import pprint

def check_for_stream(user):
    pp = pprint.PrettyPrinter(indent=1)
    a = requests.get("https://api.twitch.tv/kraken/users/{}/follows/channels".format(user))
    a = a.json()["follows"]
    channels = {}

    for channel in a:
        channels[channel["channel"]["name"]] = [channel["channel"]["name"], channel["channel"]["display_name"], channel["channel"]["url"]]

    to_return = []
    for channel in channels:
        r = requests.get("https://api.twitch.tv/kraken/streams/{}".format(channels[channel][0])).json()
        if "stream" in r:
            if r["stream"] != None:
                to_return.append([channels[channel][1], r["stream"]["game"], r["stream"]["channel"]["status"], channels[channel][2]])
        else:
            print(channel)
            pp.pprint(r)
    return to_return

