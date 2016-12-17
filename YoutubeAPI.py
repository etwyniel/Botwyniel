import requests
from os import environ


class YoutubeAPI(object):

    def __init__(self):
        self.key = environ["YOUTUBE_KEY"]


    def search_video(self, query):
        args = {"key": self.key,
                "type": "video",
                "q": query,
                "part": "snippet"}

        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=args)
        
        data = r.json()["items"]

        to_return = "https://www.youtube.com/watch?v=" + data[0]["id"]["videoId"]
        return to_return

    def get_channel_id(self, user):
        args = {"key": self.key,
                "part": "snippet",
                "q": user,
                "type": "channel"}

        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=args)
        
        channel_id = r.json()["items"][0]["id"]["channelId"]
        return channel_id

    def latest_vids(self, query, number=3):
        args = {
            "key": self.key,
            "part": "snippet",
            "channelId": self.get_channel_id(query),
            "order": "date"}
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=args)
        
        data = r.json()["items"]

        to_return = ""
        for video in range(number):
            to_return = to_return + "https://www.youtube.com/watch?v=" + data[video]["id"]["videoId"] + "\n"

        return to_return

    def get_thumbnail(self, query):
        args = {"key": self.key,
                "type": "video",
                "q": query,
                "part": "snippet"}

        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=args)

        thumbnail_url = r.json()["items"][0]["snippet"]["thumbnails"]["high"]["url"]

        return thumbnail_url
            
