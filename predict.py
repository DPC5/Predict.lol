import requests
from lol_api import getSummoner, getStats, getPuuid
from lol_api_idf import get_champion_by_key
import json

# with open('config.json', 'r') as file:
#     config = json.load(file)
# api_key = config.get('RIOT_API')

api_key = "RGAPI-7e83326b-06fb-4372-a523-d0e1a953507c"


#my puuid zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA
#test match NA1_491158594




    
def getMatches(puuid: str, count: str, region: str = "americas"):
    api_url = "https://{}.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?start=0&count={}&api_key={}".format(region, puuid, count, api_key)

    try:
        response = requests.get(api_url)
        match_list = response.json()

        filtered_match_list = []
        for match_id in match_list:
            match_details_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format(region, match_id, api_key)
            match_response = requests.get(match_details_url)
            match_data = match_response.json()
            if match_data.get('info', {}).get('gameMode') != 'ARAM':
                filtered_match_list.append(match_id)

        return filtered_match_list
    
    except requests.exceptions.RequestException as e:
        return "Error getting matches!"
print (getMatches(getPuuid("Morememes","NA1","americas"),"1"))
#print (getMatches("zHyQZrp_Jwu8TdeQ-8Q_bAkiHalERpp5HS_JFRn3VC9ZaHORdxfQgHfc3ADEWYSNvms9mqXYsVtGQA","10","americas"))
    

def getmatchDetails(match_id: str, region: str = "americas"):
    api_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format(region, match_id, api_key)

    try:
        response = requests.get(api_url)
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return ("Error getting match!")


print (getmatchDetails("NA1_4917316469"))

def getmatchStats(puuid: str, region: str = "americas", ids: list = None):

    if ids is None:
        ids = getMatches(puuid, 20, "americas")[:10]

    #init values
    total_tower_damage = 0
    total_deaths = 0
    total_kills = 0
    total_assists = 0
    total_cs = 0

    try:
        for match_id in ids:
            api_url = "https://{}.api.riotgames.com/lol/match/v5/matches/{}?api_key={}".format(region, match_id, api_key)
            response = requests.get(api_url)
            match_data = response.json()
            
            meta_data = match_data['metadata']
            index = meta_data['participants'].index(puuid) # finding puuid
            player_data = match_data['info']['participants'][index]


            total_tower_damage += player_data['damageDealtToTurrets']
            total_deaths += player_data['deaths']
            total_kills += player_data['kills']
            total_assists += player_data['assists']
            total_cs += player_data['neutralMinionsKilled'] + player_data['totalMinionsKilled']
        

        num_matches = len(ids)
        average_data = {
            "towerDamage": int(total_tower_damage / num_matches),
            "deaths": int(total_deaths / num_matches),
            "kills": int(total_kills / num_matches),
            "assists": int(total_assists / num_matches),
            "cs": int(total_cs / num_matches)
        }
        
        return average_data
    
    except requests.exceptions.RequestException as e:
        return "Error getting match!"



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

    stats = getmatchStats(puuid,"americas")
    id = getSummoner(puuid)['id']
    rank_stats = getStats(id,"na1")
    #print (rank_stats)
    tier = rank_stats['tier']
    if tier in {"UNRANKED"}:
        SR = 0
        return SR
    
    average_kills = stats['kills']
    average_deaths = stats['deaths']
    average_assists = stats['assists']
    average_cs = stats['cs']
    average_tower_damage = stats['towerDamage']


    #print (rank_stats)

    LP = rank_stats['leaguePoints']
    rank = rank_stats['rank']
    win_loss = int(rank_stats['wins']/(rank_stats['wins']+rank_stats['losses'])*100)
    if tier in {"MASTER", "GRANDMASTER", "CHALLENGER"}:
        rank = LP*0.05*lpBonus(tier)
    else:
        rank = rnC(rank)
    counter_bonus = 0


    tower_damage_bonus = average_tower_damage / 175

    #i want to reward the player for having a positive kd more than having a positive ad
    KD = (average_kills)/average_deaths # KD
    KDA_rating = ((KD/1)*10)+((average_assists/average_deaths)*2) #i want to change this to make more sense. Im just kind of guessing rn

    if tierScore(tier) > 0:
        rank_bonus = (tierScore(tier)+(rank*0.2))*5
    else:
        rank_bonus = 0

    SR = rank_bonus + counter_bonus + KDA_rating + tower_damage_bonus
    return SR

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