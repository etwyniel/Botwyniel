class VoiceEntry:
    def __init__(self, server, title, url, duration, thumbnail_url=None, message=None):
        if message != None:
            self.requester = message.author
            self.channel = message.channel
        else:
            self.requester = None
            self.channel = None
        self.server = server
        self.title = title
        self.url = url
        self.duration = duration
        self.position = 0
        self.thumbnail_url = thumbnail_url
