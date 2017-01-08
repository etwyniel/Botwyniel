from requests import get
from os import system, chdir, mkdir, getcwd

#BASE = "https://api.lootbox.eu/{platform}/{region}/"
BASE = "http://ow-api.herokuapp.com/"
#PROFILE = BASE + "{username}-{tag}/profile"
PROFILE = BASE + "profile/{platform}/{region}/{username}-{tag}"

def get_rank(battletag, region="eu"):
    username, tag = battletag.split("#")
    if len(username) > 12 or not username or len(tag) < 4:
        raise Exception("Invalid battletag")
    """
    url = PROFILE.format(platform="pc", region=region,
        username=username, tag=tag)
    print(url)
    user_data = get(url).json()
    avatar_url, level = get_avatar_and_level(battletag, region)
    if "error" in user_data:
        raise Exception("User not found")
    """
    wd = getcwd()
    scrapper = Scrapper(battletag)
    frame, level = scrapper.get_frame_and_level()
    avatar = scrapper.get_avatar()
    rank, icon = scrapper.get_rank()
    won, played = scrapper.get_won_and_played()
    """
    frame = user_data["levelFrame"]
    rank = user_data["competitive"]["rank"]
    icon = user_data["competitive"]["rank_img"]
    won = int(user_data["games"]["competitive"]["wins"])
    played = int(user_data["games"]["competitive"]["played"])
    """
    try:
        chdir("/tmp/botwyniel")
    except FileNotFoundError:
        mkdir("/tmp/botwyniel")
        chdir("/tmp/botwyniel")
    system("cp " + wd + "/background.png /tmp/botwyniel/")
    winrate = (won * 100) // played
    system("wget " + avatar + " -O avatar.png")
            #user_data["avatar"] + " -O avatar.png")
    system("wget " + frame + " -O frame.png")
    system("wget " + icon + " -O rank.png")
    system(wd + "/compose.sh " +username + " " + tag + " " +
            level + " " +  str(winrate) + " " +
           rank)
    chdir(wd)
    return "/tmp/ow_rank.png"

"""
def get_avatar_and_level(battletag, region="eu"):
    username, tag = battletag.split("#")
    if len(username) > 12 or not username or len(tag) < 4:
        raise Exception("Invalid battletag")
    url = "https://playoverwatch.com/en_us/career/{0}/{1}/{2}-{3}".format("pc",
            region, username, tag)
    page = get(url).text
    i = page.index('"player-portrait"')
    n = page[:i].rfind('"')
    avatar_url = page[page[:n].rfind('"') + 1:n]

    i = page.index('"player-level"') + 2 + len('"player-level"')
    n = page[i:].index(">") + 1 + i
    level = page[n:page[n:].index("<") + n]
    return avatar_url, level
"""

class Scrapper:
    def __init__(self, battletag, region="eu"):
        username, tag = battletag.split("#")
        self.page = get("https://playoverwatch.com/en_us/career/{0}/{1}/{2}-{3}".format("pc",
                        region, username, tag)).text

    def get_avatar(self):
        i = self.page.index('"player-portrait"')
        n = self.page[:i].rfind('"')
        return self.page[self.page[:n].rfind('"') + 1:n]

    def get_frame_and_level(self):
        i = self.page.index('"player-level"')
        n = self.page[:i].rfind(")")
        frame_url = self.page[self.page[:n].rfind("(") + 1:n]
        n = self.page[i + 2 + len('"player-level"'):].index(">") + 3 + i + len('"player-level"')
        level = self.page[n:self.page[n:].index("<") + n]
        return frame_url, level

    def get_rank(self):
        i = self.page.index('"competitive-rank"')
        i += self.page[i:].index("https://")
        icon_url = self.page[i:self.page[i:].index('"') + i]
        i += self.page[i:].index(">") + 1
        i += self.page[i:].index(">") + 1
        rank = self.page[i:self.page[i:].index("<") + i]
        return rank, icon_url

    def get_won_and_played(self, mode="competitive"):
        i = self.page.index('data-mode="{}"'.format(mode))
        i += self.page[i:].index("Games Played")
        i += self.page[i:].index("<td>") + 4
        played = int(self.page[i:i + self.page[i:].index("<")])
        i += self.page[i:].index("Games Won")
        i += self.page[i:].index("<td>") + 4
        won = int(self.page[i:i + self.page[i:].index("<")])
        return won, played
