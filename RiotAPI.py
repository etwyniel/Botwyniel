import requests
import RiotConsts as Consts


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
        winrate = self.get_winrate(name)
        return [tier, division, lp, winrate]

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
        playerIds = {}
        for player in players:
            playerIds[players[player]] = player
        api_url = Consts.URL["league"].format(
            version=Consts.API_VERSIONS["league"],
            summonerId=",".join(playerIds)
            )
        ranks = self._request(api_url)
        
        r = []
        for player in range(0, len(playerChamps), 2):
            r.append([playerChamps[player]])
            r[int(player/2)].append(playerChamps[player+1])

        for Id in playerIds.keys():
            try:
                found = False
                for queue in ranks[Id]:
                    if queue['queue'] == 'RANKED_SOLO_5x5':
                        r[int(playerChamps.index(queue["entries"][0]["playerOrTeamName"])/2)].append(queue["tier"])
                        r[int(playerChamps.index(queue["entries"][0]["playerOrTeamName"])/2)].append(queue["entries"][0]["division"])
                        found = True
                if not found:
                    r[int(playerChamps.index(playerIds[Id])/2)].append("unranked")
            except Exception as e:
                r[int(playerChamps.index(playerIds[Id])/2)].append("unranked")
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

    def get_winrate(self, name, season="SEASON2016"):
        summoner_id=self.get_summoner_by_name(name)[name.lower()]["id"]

        api_url = Consts.URL["statistics_summary"].format(
            region=self.region,
            summoner_id=summoner_id,
            version=Consts.API_VERSIONS["statistics"])
        
        args = {
            "season": season,
            "api_key": self.api_key
            }
        
        r = requests.get(
            Consts.URL["base"].format (
                proxy=self.region,
                region=self.region,
                url=api_url
                 ),
            params=args
            ).json()

        for queue in r["playerStatSummaries"]:
            if queue["playerStatSummaryType"] == "RankedSolo5x5":
                wins = queue["wins"]
                losses = queue["losses"]
                total_games = wins + losses
        if total_games != 0:
            winrate = wins / total_games

        return round(winrate * 100)
            
