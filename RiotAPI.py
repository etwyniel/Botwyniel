import requests
import RiotConsts as Consts
from datetime import datetime, date
import os

if not os.path.isdir("logs"):
    os.makedirs("logs")
os.chdir("logs")


def log(event):
    log = open("{date}.dat".format(
    date=str(date.today())
    ),
               "a")
    log.write("[{time}] {event}\n\n".format(
        time="".join(str(datetime.now().time()).split(".")[0])[0:5],
        event=str(event)
        )
    )
    log.close()


class RiotAPI(object):
    def __init__(self, api_key, region=Consts.REGIONS["europe_west"]):
        self.api_key = api_key
        self.region = region

    def _request(self, api_url, params={}):
        args = {"api_key": self.api_key}
        for key, value in params.items():
            if key not in args:
                args[key] = value
        response = requests.get(
            Consts.URL["base"].format(
                proxy=self.region,
                region=self.region,
                url=api_url
                ),
            params=args
            )

        a = response
        log(str(Consts.URL["base"].format(
                proxy=self.region,
                region=self.region,
                url=api_url
                )
                ) + " " + str(a)
            )
        return response.json()

    def get_summoner_by_name(self, name):
        api_url = Consts.URL["summoner_by_name"].format(
            version=Consts.API_VERSIONS["summoner"],
            names=name
            )
        return self._request(api_url)

    def get_summoner_rank(self, name):
        summonerId = self.get_summoner_by_name(name)[name.lower()]["id"]
        api_url = Consts.URL["league"].format(
            version=Consts.API_VERSIONS["league"],
            summonerId=summonerId
            )
        league = self._request(api_url)
        tier = league[str(summonerId)][0]["tier"]
        division = league[str(summonerId)][0]["entries"][0]["division"]
        lp = league[str(summonerId)][0]["entries"][0]["leaguePoints"]
        return [tier, division, lp]

    def get_summoner_level(self, name):
        api_url = Consts.URL["summoner_by_name"].format(
            version=Consts.API_VERSIONS["summoner"],
            names=name
            )
        return self._request(api_url)[name.lower()]["summonerLevel"]

    def get_game_ranks(self, name, params={}):
        summonerId = self.get_summoner_by_name(name)[name.lower()]["id"]
        args = {"api_key": self.api_key}
        for key, value in params.items():
            if key not in args:
                args[key] = value
        response = requests.get(
            Consts.URL["current_game"].format(
                proxy=self.region,
                platformId=Consts.PLATFORM_IDS[self.region],
                summonerId=summonerId
                ),
            params=args
            )
        
        a = response
        log(str(Consts.URL["current_game"].format(
                proxy=self.region,
                platformId=Consts.PLATFORM_IDS[self.region],
                summonerId=summonerId
                )
                ) + " " + str(a)
            )
        a = response

        if str(response) == "<Response [200]>":
            print("Request OK.")
        elif str(response) == "<Response [404]>":
            print("Player not in game.")
            return False
        game = response.json()
        players = {}
        playerNames = []
        playerChamps = []
        for player in game["participants"]:
            if player["teamId"] == 100:
                playerNames = [player["summonerName"]] + playerNames
                playerChamps = [player["summonerName"], Consts.CHAMPIONS_BY_ID[player["championId"]]] + playerChamps
            else:
                playerNames = playerNames + [player["summonerName"]]
                playerChamps = [player["summonerName"], Consts.CHAMPIONS_BY_ID[player["championId"]]] + playerChamps
            players[player["summonerName"]] = str(player["summonerId"])
        playerIds = list(players.values())
        api_url = Consts.URL["league"].format(
            version=Consts.API_VERSIONS["league"],
            summonerId=",".join(playerIds)
            )
        ranks = self._request(api_url)
        
        r = []
        for player in range(0, len(playerChamps), 2):
            r.append([playerChamps[player]])
            r[int(player/2)].append(playerChamps[player+1])
        for Id in playerIds:
            try:
                r[playerNames.index(ranks[Id][0]["entries"][0]["playerOrTeamName"])].append(ranks[Id][0]["tier"])
                r[playerNames.index(ranks[Id][0]["entries"][0]["playerOrTeamName"])].append(ranks[Id][0]["entries"][0]["division"])
            except:
                r[playerNames.index(ranks[Id][0]["entries"][0]["playerOrTeamName"])].append("unranked")
        return r

    def get_free_champions(self):
        api_url = Consts.URL["free_champions"].format(
            region=self.region
            )
        args = {"freeToPlay": "true", "api_key": self.api_key}
        response = requests.get(
            Consts.URL["base"].format(
                proxy=self.region,
                region=self.region,
                url=api_url
                ),
            params=args
            )
        r = response.json()
        champions = []
        for champ in r["champions"]:
            champions.append(Consts.CHAMPIONS_BY_ID[champ["id"]])
        return champions
            
