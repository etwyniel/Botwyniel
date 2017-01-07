from requests import get
from os import system, chdir, mkdir, getcwd

BASE = "https://api.lootbox.eu/{platform}/{region}/"
PROFILE = BASE + "{username}-{tag}/profile"

def get_rank(battletag, region="eu"):
    username, tag = battletag.split("#")
    if len(username) > 12 or not username or len(tag) < 4:
        raise Exception("Invalid battletag")
    url = PROFILE.format(platform="pc", region=region,
        username=username, tag=tag)
    print(url)
    user_data = get(url).json()
    if "error" in user_data:
        raise Exception("User not found")
    wd = getcwd()
    try:
        chdir("/tmp/botwyniel")
    except FileNotFoundError:
        mkdir("/tmp/botwyniel")
        chdir("/tmp/botwyniel")
    system("cp " + wd + "/background.png /tmp/botwyniel/")
    winrate = (int(user_data["data"]["games"]["competitive"]["wins"]) * 100) // \
        int(user_data["data"]["games"]["competitive"]["played"])
    system("wget " + user_data["data"]["avatar"] + " -O avatar.png")
    system("wget " + user_data["data"]["levelFrame"] + " -O frame.png")
    system("wget " + user_data["data"]["competitive"]["rank_img"] + " -O rank.png")
    system(wd + "/compose.sh " + user_data["data"]["username"] + " " + tag + " " +
            str(user_data["data"]["level"]) + " " +  str(winrate) + " " +
           user_data["data"]["competitive"]["rank"])
    chdir(wd)
    return "/tmp/ow_rank.png"
