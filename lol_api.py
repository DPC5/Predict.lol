import requests
from lol_api_idf import get_champion_by_key
import concurrent.futures
import json

# with open('config.json', 'r') as file:
#     config = json.load(file)
# api_key = config.get('RIOT_API')

api_key = "RGAPI-cf146074-5698-4558-98e9-ca55f32c7591"



# TODO Make it so I can grab more matches 
# After make it so that everyone is atleast able to have an SR
# Accurancy right now is close to around 75% which is fine
# Im not happy with the tuner yet I waant to make it a bit closer, maybe calculating average dragon/baron
# And average cs woulld be nice



#getting account name and tagline by puuid

def getAccountTag(puuid: str, region: str = "americas"): #grabs account name and tag by puuid
    api_url = "https://{}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{}?api_key={}".format(region,puuid,api_key)

    try:

        response = requests.get(api_url)
        player_info = response.json()
        return "{}#{}".format(player_info['gameName'],player_info['tagLine'])

    except requests.exceptions.RequestException as e:
        return("Error getting account tag!")


def getPuuid(name: str, tag: str, region: str = "americas"): # gets the puuid from a riot tag uses new regions (ex: americas)
    api_url = "https://{}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}".format(region,name,tag,api_key)

    try:
        response = requests.get(api_url)
        account_info = response.json()
        #print (account_info)
        return account_info['puuid']
    
    except requests.exceptions.RequestException as e:
        return("Error getting puuid!")


#print (getPuuid("GodBlonde","5499","americas"))
#print (getPuuid("Morememes","NA1","americas"))
#print (getPuuid("The Driver","robot"))

#get summoner

def getSummoner(puuid: str, region: str = "na1"): #grabs summoner data WARNING USES OLDER REGION TAGS
    api_url = "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{}?api_key={}".format(region,puuid,api_key)

    try:
        response = requests.get(api_url)
        return response.json()

        #allowed responses 
        # 'id'
        # 'accoundId'
        # 'puuid'
        # 'name'
        # 'profileIconId'
        # 'revisionDate'
        # 'summonerLevel'
        


    except requests.exceptions.RequestException as e:
        return("Error getting summoner!")


#print (getSummoner("odrM1Qv3RXmjHC_-EDuAVYUSfFFkbrzcbdRiqtYHhmKXWDrHTo4RHxfS9jU_jN92t6cDJolu3g6PGA")['id'])
#print (getSummoner("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA")['id'])
#print (getSummoner("tWIXuVh_yeQbixe2DVg-8nvAf7IkwEH_NriaT2G-kX7Rt0AjUhskd1NsBtv1hl_ExBCL2K0pnIYb1w")['id'])

#get rank

def getStats(id: str, region: str = "na1"): #get account game stats BY ID NOT PUUID
    api_url = "https://{}.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}".format(region,id,api_key)

    try:
        response = requests.get(api_url)
        response = response.json()

        if response:
            return response[0]        
        else:
            response = {
                "tier": "UNRANKED",
                "rank": "",
                "wins": 0,
                "losses": 0,
                "leaguePoints": 0 
            }
            return response
    
        # example responses 
        # "leagueId": "3a342298-b1a0-4ab3-966c-5972c807a01f",
        # "queueType": "RANKED_SOLO_5x5",
        # "tier": "SILVER",
        # "rank": "II",
        # "summonerId": "FJ_3CABngRZ_7nBggFR3zAIp7lrMZVnY3DItxS1LtytQpKMa",
        # "summonerName": "Morememes",
        # "leaguePoints": 37,
        # "wins": 13,
        # "losses": 13,
        # "veteran": false,
        # "inactive": false,
        # "freshBlood": false,
        # "hotStreak": false
    
    except requests.exceptions.RequestException as e:
        return("Error getting game stats!")
#print (getStats(getSummoner(getPuuid("The Driver","robot"))['id']))
#print (getStats("bZEzyw9zHqgtk3LWkmEs7d0Zqf7ioC3Qk5n1Pxu76gPKgM6W","na1"))
#print (getStats("kJd6IFeOBTZ8j-tuRAv3Ny1dpFm-dMTiB6Z_zi_WPLpCn4iQvb-agxESTg"))

#mastery handling 

def getMastery(puuid: str, count: int = 1): #returns mastery for champ(s) in count
    api_url = "https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{}/top?api_key={}&count={}".format(puuid,api_key,count)

    try:

        response = requests.get(api_url) #grabbing response of the api
        response.raise_for_status() #checking for error 4 or 5xx code
        mastery_info = response.json()

        champion_names = []
        for mastery in mastery_info:
            champion_id = mastery['championId']
            champion_name = get_champion_by_key(champion_id, "en_US")['name']
            champion_names.append(champion_name)

        return champion_names
        #this returns a dictonary of champs, to locate do [x] x being the number in highest to lowest champ to select

    except requests.exceptions.RequestException as e:
        return("Error getting mastery!")

# print (getMastery("mBTJkW5vuRHVSd2KmutqtpTv9-vU7tkVcEmxba7iwImElgbx5z6mbGn8DbA9HN9WZ0ob7cZWhbBBwg", 2)) #debug
    


#gets information on the current match that the user is in
#requires Sumonerid
def getMatch(id: str, region = "na1"):
    api_url = "https://{}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{}?api_key={}".format(region, id, api_key)

    try:
        response = requests.get(api_url)
        return response
    except requests.exceptions.RequestException as e:
        return ("Error getting match!")
    
#print (getSummoner(getPuuid("Morememes","na1"))['id'])
#print (getMatch(getSummoner(getPuuid("Morememes","na1"))['id']))
    

def extract_player_roles(match_details: str):
    if match_details is None:
        return None
    roles = {}
    if "info" in match_details and "participants" in match_details["info"]:
        for participant in match_details["info"]["participants"]:
            summoner_name = participant["summonerName"]
            puuid = participant["puuid"]
            role = participant["individualPosition"]
            roles[summoner_name] = {"role": role, "puuid": puuid}
    return roles



#my puuid zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA
#test match NA1_491158594
    
def getMatches(puuid: str, count: str, region: str = "americas"):
    api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}&api_key={api_key}"

    try:
        response = requests.get(api_url)
        match_list = response.json()

        filtered_match_list = []

        # Function to fetch match details and filter out non-ranked matches
        def fetch_match(match_id):
            match_details_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
            match_response = requests.get(match_details_url)
            match_data = match_response.json()
            game_mode = match_data.get('info', {}).get('gameMode')
            if game_mode == 'CLASSIC' or game_mode == 'RANKED':
                return match_id
            else:
                return None

        # Fetch match details concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_match, match_id) for match_id in match_list]
            concurrent.futures.wait(futures)

            # Collect filtered match IDs
            for future in futures:
                match_id = future.result()
                if match_id:
                    filtered_match_list.append(match_id)

        return filtered_match_list

    except requests.exceptions.RequestException as e:
        print(f"Error getting matches: {e}")
        print (match_list)
        return []


#print (getMatches("e7CCYZ2S7U6cKBTjesuTD3kAPyc2H-YsBhDmQ7J6_b5PnRsN2n4XD39ZZv6thlb1XPv27Dvd2rXueg","2")) 
#print (getMatches(getPuuid("katevolved","666","americas"),"1"))
#print (getPuuid("Morememes","NA1"))
#print (getMatches("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA","2"))
#print (getMatches("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA","10","americas"))
    

def getmatchDetails(match_id: str, region: str = "americas"):
    api_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format(region, match_id, api_key)

    try:
        response = requests.get(api_url)
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return ("Error getting match!")


#print (getmatchDetails("NA1_4917316469"))
#print (extract_player_roles(getmatchDetails("NA1_4917316469")))


#getting invalid match data because if within the count provided no ranked or normal games are played
#it will not return the match data
#if only have played aram or urf it will return an error

def getmatchStats(puuid: str, region: str = "americas", ids: list = None):
    if ids is None:
        ids = getMatches(puuid, 1, region)[:1]

    total_tower_damage = 0
    total_deaths = 0
    total_kills = 0
    total_assists = 0
    total_cs = 0

    try:
        def fetch_match_data(match_id):
            try:
                api_url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}"
                response = requests.get(api_url)
                match_data = response.json()

                meta_data = match_data['metadata']
                index = meta_data['participants'].index(puuid)
                player_data = match_data['info']['participants'][index]

                return {
                    "towerDamage": player_data['damageDealtToTurrets'],
                    "deaths": player_data['deaths'],
                    "kills": player_data['kills'],
                    "assists": player_data['assists'],
                    "cs": player_data['neutralMinionsKilled'] + player_data['totalMinionsKilled']
                }
            except Exception as e:
                print(f"Error fetching match {match_id}: {e}")
                return None

        with concurrent.futures.ThreadPoolExecutor() as executor:
            match_data_list = list(executor.map(fetch_match_data, ids))

        num_matches = len(match_data_list)
        for match_data in match_data_list:
            if match_data:
                total_tower_damage += match_data['towerDamage']
                total_deaths += match_data['deaths']
                total_kills += match_data['kills']
                total_assists += match_data['assists']
                total_cs += match_data['cs']

        if num_matches > 0:
            average_data = {
                "towerDamage": int(total_tower_damage / num_matches),
                "deaths": int(total_deaths / num_matches),
                "kills": int(total_kills / num_matches),
                "assists": int(total_assists / num_matches),
                "cs": int(total_cs / num_matches)
            }
            return average_data
        else:
            average_data = {
                "towerDamage": 0,
                "deaths": 0,
                "kills": 0,
                "assists": 0,
                "cs": 0
            }
            print ("No valid match data")
            return average_data

    except requests.exceptions.RequestException as e:
        average_data = {
                "towerDamage": 0,
                "deaths": 0,
                "kills": 0,
                "assists": 0,
                "cs": 0
            }
        print (f"Error getting match: {e}")
        print (match_data)
        return average_data




#print (getmatchStats("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA","americas"))

#SUMMONER RATING CALCULATION

#roman numeral converter really shitty but funny
def rnC(input: str = None):
    if input is not None:
        con = input
        con = con.replace("IV","1")
        con = con.replace("III","2")
        con = con.replace("II","3")
        con = con.replace("I","4")
        return int(con)
    else:
        return 0

#adds a bonus to being a higher rank, however if they are unranked this bonus is ignored
def tierScore(tier: str = None):
    tier_scores = {
        "CHALLENGER": 32,
        "GRANDMASTER": 24,
        "MASTER": 20,
        "DIAMOND": 14,
        "EMERALD": 10,
        "PLATINUM": 7,
        "GOLD": 4,
        "SILVER": 3,
        "BRONZE": 2,
        "IRON": 1
    }
    return tier_scores.get(tier, 0) 

#applying a bonus for lp in the apex tiers
def lpBonus(tier: str):
    lp_bonus = {
        "CHALLENGER": 2.5,
        "GRANDMASTER": 2,
        "MASTER": 1,
    }
    return lp_bonus.get(tier, 0)

#find what basic champion roles counter the other
#will probally need more looking into maybe even subclasses
#and possibly role they champion is being played in
def counterCalc(role1: str, role2: str):
    counters = {
        "tank": ["fighter", "marksman"],
        "controller": ["fighter", "slayer"],
        "slayer": ["tank"],
        "mage": ["slayer", "tank"],
        "marksman": ["mage"],
        "fighter": ["marksman"]

    }


#main calculation for SR
def calcSR(puuid: str = None):
    print ("calc sr {}".format(puuid))
    try:
        stats = getmatchStats(puuid, "americas")
        #print (stats)
        id = getSummoner(puuid)['id']
        rank_stats = getStats(id, "na1")
        tier = rank_stats['tier']
        #print ("pass1")
        if tier == "UNRANKED":
            return 0

        LP = rank_stats['leaguePoints']
        #print ("pass2")
        wins = rank_stats['wins']
        #print ("pass3")
        losses = rank_stats['losses']
        #print ("pass4")
        rank = rank_stats['rank']
        #print ("pass5")
        average_kills = stats['kills']
        #print ("pass6")
        average_deaths = stats['deaths']
        #print ("pass7")
        average_assists = stats['assists']
        #print ("pass8")
        average_tower_damage = stats['towerDamage']
        #print ("pass9")
        average_cs = stats['cs']
        #print ("pass10")
        win_loss = wins / (wins + losses) * 100

        if tier in {"MASTER", "GRANDMASTER", "CHALLENGER"}:
            rank = LP * 0.05 * lpBonus(tier)
        else:
            rank = rnC(rank)


#all of these can be changed to make certain stats more important or not
        tower_damage_bonus = average_tower_damage / 175
        KD = average_kills / average_deaths
        KDA_rating = ((KD / 1) * 10) + ((average_assists / average_deaths) * 2)
        CS_bonus = average_cs / 50

        if tierScore(tier) > 0:
            rank_bonus = (tierScore(tier) + (rank * 0.2)) * 5
        else:
            rank_bonus = 0
        SR = int(rank_bonus + tower_damage_bonus + KDA_rating + CS_bonus )
        if SR is None:
            SR = 0
        return SR
    except Exception as e:
        print(f"Error calculating SR: {e}")
        return 0


#print (calcSR("UuwOjWkWG6ohdzsnIeUIDvREDPzW9EqY6VBArX9lbkXBM7rXdIM1yFbRVixkp_RlGgikzLJEdVnU7w"))

#this is prob just gonna be wrong but who care rn

def calcPercent(SR1: int, SR2: int):

    blue_side_bias = 25
    SR1 = SR1 + blue_side_bias
    if SR1 > SR2:
        winner = "Blue Side"
    elif SR1 == SR2:
        winner = "Coin Flip"
    else:
        winner = "Red Side"
    if (max(SR1, SR2))/(min(SR1, SR2))*50 > 100:
        chance = 100
    else:
        chance = (max(SR1, SR2))/(min(SR1, SR2))*50
    calc = {
        "winner": winner,
        "chance": chance
    }
    return calc




#print (calcPercent(62.84571428571428*5,112.84571428571428+62.462*4))
#print (calcSR(getPuuid("The Driver","robot")))

#print (calcSR(getPuuid("Morememes","NA1")))





#print (getmatchDetails("NA1_4920877607"))
#print (extract_player_roles(getmatchDetails("NA1_4917316469")))


# Main problem looks like rate limit is begin exceded
# to get around this I will try to break the prediction into two parts then add

# #main error when predicting matches
# Error fetching match NA1_4917730925: 'metadata'
# Error fetching match NA1_4917771608: 'metadata'
# Error fetching match NA1_4917812460: 'metadata'
# Error calculating SR: division by zero
# calc sr Te5q6seXlnuFr-anG56Vsc9FQyAUQRC47vM-ZAJ2ezhm8MZNzFJIGLdXOLHh2OZUhQlDthQVFjhgbw
# Error calculating SR: string indices must be integers, not 'str'
# calc sr LMbyUUjiNndegs4_8decr8PyZJOk5pOLMPBteWR5L_at7esDdlRNxCIYC6V54WacuQu4Oc558yNJKA
# Error calculating SR: string indices must be integers, not 'str'
# calc sr Jwoy5n9iD0ETsKGbojK4nbMys6xbnlvXAOhTStHfvmzI2TNxynFeIBgu_9oe5yI3RHfhgE2SFH8n_g
# Error calculating SR: string indices must be integers, not 'str'
# calc sr Jc5EvvhGeOd3M7YIeljqxvwq8OhwvZQiv-KlOcWKYSFo-hAyzopnzxysmdpkB12c8iF3nNYRCZhL0Q
# Error calculating SR: string indices must be integers, not 'str'