import requests


class YoutubeAPI(object):

    def __init__(self, query):
        self.query = query
        self.key = "AIzaSyAAd6n7iBmyuVwzLZEQCS3IxYVz2I8Hl5Q"


    def search_video(self):
        args = {"key": self.key,
                "type": "video",
                "q": self.query,
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

    def latest_vids(self, number=3):
        args = {
            "key": self.key,
            "part": "snippet",
            "channelId": self.get_channel_id(self.query),
            "order": "date"}
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=args)
        
        data = r.json()["items"]

        to_return = ""
        for video in range(number):
            to_return = to_return + "https://www.youtube.com/watch?v=" + data[video]["id"]["videoId"] + "\n"

        return to_return

    def get_thumbnail(self):
        args = {"key": self.key,
                "type": "video",
                "q": self.query,
                "part": "snippet"}

        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params=args)

        thumbnail_url = r.json()["items"][0]["snippet"]["thumbnails"]["high"]["url"]

        return thumbnail_url
            
