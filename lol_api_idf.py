import requests

champion_by_id_cache = {}
champion_json = {}

def get_latest_champion_ddragon(language="en_US"): #pulls list of updated champion info
    if language in champion_json:
        return champion_json[language]

    version_index = 0
    while True:
        version_response = requests.get("http://ddragon.leagueoflegends.com/api/versions.json")
        version_data = version_response.json()
        version = version_data[version_index]

        response = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/champion.json")

        if response.ok:
            champion_json[language] = response.json()
            return champion_json[language]

        version_index += 1

def get_champion_by_key(key, language="en_US"): #returns everything about a champ
    if language not in champion_by_id_cache:
        json_data = get_latest_champion_ddragon(language)
        champion_by_id_cache[language] = {champ_info["key"]: champ_info for champ_info in json_data["data"].values()}

    return champion_by_id_cache[language].get(str(key))

def get_champion_by_id(name, language="en_US"):
    return get_latest_champion_ddragon(language)["data"].get(name)

#print (get_champion_by_key(777))


# get summoner icon

def get_summoner_icon(id: int):
    version_index = 0
    version_response = requests.get("http://ddragon.leagueoflegends.com/api/versions.json")
    version_data = version_response.json()
    version = version_data[version_index]

    return "https://ddragon.leagueoflegends.com/cdn/{}/img/profileicon/{}.png".format(version,id)

