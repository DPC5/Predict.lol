
import discord
from discord.ext import commands
from lol_api import getPuuid, getAccountTag, getSummoner, getMastery, getStats, calcSR, extract_player_roles, getmatchDetails, calcPercent
# from predict import calcSR, calcPercent
from lol_api_idf import get_summoner_icon
import json
import datetime
import asyncio
import os
data_file = 'data.json'





with open('config.json', 'r') as file:
    config = json.load(file)
token = config.get('token')
RIOT_API = config.get('RIOT_API')

bot = commands.Bot(command_prefix="^", intents = discord.Intents.all())


with open(data_file, 'r') as f:
    data = json.load(f)


ver = data['version']
opgg_image_path = r"C:\Users\danny\Desktop\code\python\discord\opgg.png"


bot.remove_command('help')


@bot.event
async def on_ready():
    asyncio.create_task(update_activity())
    print(f'Logged in as {bot.user}')


async def update_activity():
    while True:
        predicts = data['predict']
        await bot.change_presence(activity=discord.Streaming(name="{} Predictions".format(predicts), url="https://www.twitch.tv/morememes_"))
        await asyncio.sleep(30)


@bot.command()
async def info(ctx):
    embed=discord.Embed(title=" ", description="Version {} By Morememes".format(ver))
    embed.set_author(name="ChoBot")
    embed.add_field(name="What does it do?", value="This bot was made as a test to see a couple things. First, if I could make a functioning bot. Second, can I make a program that has some connection to a game I play.", inline=False)
    embed.add_field(name="What is SR?", value="SR or Summoner Rating, is a number that gives an estimate to how much positive inpact a player has on their game. ", inline=False)
    embed.add_field(name="How is SR calculated?", value="SR is calculated right now by taking average stats over the past 10 games and comparing them with your rank. These stats include damage, tower damage, kda, and more. In a game SR will be dynamic, this means it will calculate whether the draft of that game makes you more impactful or makes the enemy more impactful. Expect SR around 125 to be high impact players im most of their games.", inline=False)
    embed.add_field(name="Why is somone's SR so high?", value="SR has two values, the main one being general SR this is what is displayed using ^lookup. This value is the impact that the player would have on an average game with ranging skill levels. The next SR is hidden, this will only be seen when ranks are close together. This SR will no longer apply bonuses based on rank, it will only apply bonuses based on LP. This is mainly prevelant in higher elo.", inline=False)
    embed.add_field(name="More?", value="If you have any suggestions please message me on discord. Also, keep in mind this is my first discord bot and first semi-public program, there will be bugs please be patient.", inline=False)
    await ctx.send(embed=embed)



#LOL API integration using my library

def fName(name: str):
    if "+" in name:
        name = name.split("+")
        tag = name[1]
        name = name[0]+" "+tag.split("#")[0]
        tag = tag.split("#")[1]
    else:
        split = name.split("#")
        name = split[0]
        tag = split[1]
    info = {
        "name": name,
        "tag": tag
    } 
    return info



@bot.command()
async def lookup(ctx, name: str = None):
    print ("Lookup command recieved!")
    channel = ctx.channel

    if name is None:
        await channel.send('Please input a valid name')
        return

    #make it so that spaces in names can be done with + 
    #because i dont know how to do it anyother way
    #try to fix  the time out / optimize later
    #it takes almost 10-20 seconds to post result
    info = fName(name) 
    name = info['name']
    tag = info['tag']
    if "+" in name:
        opurl = "https://www.op.gg/summoners/na/{}-{}".format(name.replace(" ","%20"),tag) # gotta fix the url for accounts with spaces
    else:
        opurl = "https://www.op.gg/summoners/na/{}-{}".format(name,tag) # had to change url for accounts without spaces
    region = "americas"
    region2 = "na1"

    puuid = getPuuid(name,tag,region)
    

    file = discord.File(opgg_image_path, filename="opgg.png")
    account_tag = getAccountTag(puuid,region)
    summoner = getSummoner(puuid,region2)
    icon = get_summoner_icon(summoner['profileIconId'])
    level = summoner['summonerLevel']
    top_champ = getMastery(puuid, 1)[0]
    id = summoner['id']
    stats = getStats(id,region2)

    if stats['tier'] in {"UNRANKED", "MASTER", "GRANDMASTER", "CHALLENGER"}:
        rank = ""
    else:
        rank = stats['rank']

    rank = "{} {} {} LP".format(stats['tier'],rank,stats['leaguePoints'])
    if stats['losses'] == 0:
        wr = 0
    else:
        wr = int(stats['wins']/(stats['wins']+stats['losses'])*100)
                 
    win_loss = "{} | {} (%{} Win Rate)".format(stats['wins'],stats['losses'],wr)
    if stats['tier'] not in {"UNRANKED"}:
        sr = calcSR(puuid)
    else:
        sr = 0



    embed=discord.Embed(title=" ")
    embed.set_author(name=account_tag, url=opurl, icon_url="attachment://opgg.png")
    embed.set_thumbnail(url=icon)
    embed.add_field(name="Level", value=level, inline=True)
    embed.add_field(name="Rank", value=rank, inline=True)
    embed.add_field(name="Top Champion", value=top_champ, inline=True)
    embed.add_field(name="Win/Loss", value=win_loss, inline=True)
    embed.add_field(name="SR", value=sr, inline=True)
    await ctx.send(file=file, embed=embed)
    print ("Lookup command sent!")


@bot.command()
@commands.cooldown(1, 120, commands.BucketType.guild)
async def predict(ctx, input: str):
    print ("predicting ....")


    # data['predict'] += 1

    # with open(data_file, 'w') as f:
    #     json.dump(data, f, indent=4)

    now = datetime.datetime.now()
    now = now.strftime("%I:%M %p")
    
    channel = ctx.channel

    region = "americas"
    region2 = "na1"

    players = extract_player_roles(getmatchDetails(input))
    
    blueside = {}
    redside = {}

    for index, (name, data) in enumerate(players.items()):
        if index < 5:
            blueside[name] = {'puuid': data['puuid'], 'name': name}
        else:
            redside[name] = {'puuid': data['puuid'], 'name': name}


    roles = [
        'TOP',
        'JUNGLE',
        'MID',
        'BOT',
        'SUPPORT'
    ]

    # Constructing the embed message
    print (list(blueside.keys()))
    bs = list(blueside.keys())
    rs = list(redside.keys())
    bsrT = 0
    rsrT = 0
    bsr = []
    rsr = []
    for i in range(5):
        bsr.append(calcSR(blueside[list(blueside.keys())[i]]['puuid']))
        bsrT += bsr[i]
        rsr.append(calcSR(redside[list(redside.keys())[i]]['puuid']))
        rsrT += rsr[i]
    embed=discord.Embed(title="TEST MATCH", description="**Winner: {} (%{})**".format(calcPercent(bsrT,rsrT)['winner'],int(calcPercent(bsrT,rsrT)['chance'])), color=0x0000ff)
    for i in range (5):
        embed.add_field(name="{} ({})".format(roles[i], bs[i]), value='''SR {}'''.format(bsr[i]), inline=True)
        embed.add_field(name = chr(173), value = chr(173), inline=True)
        embed.add_field(name="{} ({})".format(roles[i], rs[i]), value='''SR {}'''.format(rsr[i]), inline=True)
    if bsrT + rsrT < 200:
        warning = "*WARNING LOW TOTAL SR*"
    else:
        warning = ""
    embed.set_footer(text="ALPHA TEST GENERATED: {} {}".format(now,warning))
    await ctx.send(embed=embed)
    print ("Predict sent...")

@predict.error
async def predict_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f} seconds before making another prediction.")

bot.run(token)