from json.decoder import JSONDecodeError
import os
import json
from sys import platform
from datetime import date, datetime, timedelta
from discord.ext.commands.errors import MissingRequiredArgument
from dotenv import load_dotenv
from discord.ext import commands, tasks

##Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('CHANNEL')
JSON_FILE = os.getenv('JSON_FILE')
SUCCESS_EMOJI = os.getenv('SUCCESS_EMOJI')
FAIL_EMOJI = os.getenv('FAIL_EMOJI')

if SUCCESS_EMOJI is None:
    SUCCESS_EMOJI = '\u2705'
if FAIL_EMOJI is None:
    FAIL_EMOJI = '\u26D4'
WEEKLY_CHECK_DAY = os.getenv('WEEKLY_CHECK_DAY')
try:
    WEEKLY_CHECK_DAY = int(WEEKLY_CHECK_DAY)
except TypeError:
    WEEKLY_CHECK_DAY = 6

log = {}
try: 
    with open(JSON_FILE, 'r') as openfile:
        log = json.load(openfile)
except FileNotFoundError:
    openfile = open(JSON_FILE, 'x')
    openfile.close()
except JSONDecodeError:
    pass
bot = commands.Bot(command_prefix='!')

##Commands
@bot.command(name='all', help='Shows everyone\'s resolution')
async def all(ctx):
    if ctx.channel.id != int(CHANNEL):
        return
    try:
        for user in log:
            await ctx.send(f'{log[user]["name"]}: {log[user]["resolution"]} | {"Daily" if log[user]["daily"] else "Weekly"} | Last Update: {date_format(datetime.strptime(log[user]["update_date"], "%Y-%m-%d").date())}')
    except:
        pass

@bot.command(name='res', help='Shows your resolution and status')
async def resolution(ctx):
    if ctx.channel.id != int(CHANNEL):
        return
    try: 
        user_info = log[str(ctx.author.id)]
        await ctx.send(f'{user_info["mention"]}\'s resolution: {user_info["resolution"]} | {"Daily" if user_info["daily"] else "Weekly"}\nMost Recent Update: \"{user_info["update"]}\" on {date_format(datetime.strptime(user_info["update_date"], "%Y-%m-%d").date())}')
    except KeyError: 
        await ctx.send('You don\'t have a resolution! use !set to make one')

@bot.command(name='set', help='Sets your resolution for 2022. ex: !set "Eat Healthy"')
async def set_resolution(ctx, resolution: str):
    if ctx.channel.id != int(CHANNEL):
        return
    id = str(ctx.author.id)
    log[id] = {}
    log[id]['resolution'] = resolution
    log[id]['name'] = ctx.author.name
    log[id]['mention'] = '<@'+str(ctx.author.id)+'>'
    log[id]['update'] = ''
    log[id]['update_date'] = date.today().isoformat()
    log[id]['daily'] = False
    response=resolution
    dump_json()
    await ctx.send(f'{ctx.author.name}\'s New Year Resolution: ' + response)

@bot.command(name='update', help='Tells everyone any updates on your resolution. ex: !updated "this is my update today"')
async def update_resolution(ctx, update: str):
    if ctx.channel.id != int(CHANNEL):
        return
    try:
        log[str(ctx.author.id)]['update'] = update.strip()
        log[str(ctx.author.id)]['update_date'] = date.today().isoformat()
        dump_json()
        await ctx.send(f'Thanks for updating us {ctx.author.name}!')
    except MissingRequiredArgument:
        await ctx.send(f'Put an update ( !update "this is my update today")')
    except KeyError:
        await ctx.send('You don\'t have a resolution! use !set to make one')

@bot.command(name='daily', help='Sets bot to check-in daily')
async def set_daily_mode(ctx):
    if ctx.channel.id != int(CHANNEL):
        return
    try:
        log[str(ctx.author.id)]['daily'] = True
        dump_json()
        await ctx.send(f'{ctx.author.name} is checking in daily!')
    except KeyError:
        await ctx.send('You don\'t have a resolution! use !set to make one')

@bot.command(name='weekly', help='Sets bot to check-in weekly')
async def set_weekly_mode(ctx):
    if ctx.channel.id != int(CHANNEL):
        return
    try:
        log[str(ctx.author.id)]['daily'] = False
        dump_json()
        await ctx.send(f'{ctx.author.name} is checking in weekly!')
    except KeyError:
        await ctx.send('You don\'t have a resolution! use !set to make one')

##Tasks
@tasks.loop(hours=24)
async def announce_statuses():
    DAILY_DELTA = date.today()-timedelta(days=1)
    WEEKLY_DELTA = date.today()-timedelta(days=7)
    channel = await bot.fetch_channel(int(CHANNEL))
    if date.today().weekday() == WEEKLY_CHECK_DAY:
        await channel.send(f'Weekly Resolution Results {date_format(WEEKLY_DELTA)} - {date_format(date.today())}: ')
    else:
        await channel.send(f'Daily Resolution Results {date_format(date.today())}: ')
    for user in log:
        if date.today().weekday() == WEEKLY_CHECK_DAY and log[user]['daily'] == False: 
            if date.fromisoformat(log[user]['update_date']) > WEEKLY_DELTA:
                await channel.send(f'{log[user]["mention"]} {SUCCESS_EMOJI}')
            else:
                await channel.send(f'{log[user]["mention"]} {FAIL_EMOJI}')
        elif log[user]['daily'] == True: 
            if date.fromisoformat(log[user]['update_date']) > DAILY_DELTA:
                await channel.send(f'{log[user]["mention"]} {SUCCESS_EMOJI}')
            else:
                await channel.send(f'{log[user]["mention"]} {FAIL_EMOJI}')

##Helpers
def dump_json():
    json_object = json.dumps(log, indent = 4)
    with open(JSON_FILE, 'w') as outfile:
        outfile.write(json_object)

def date_format(date: date):
    if platform == "win32" or platform == "cygwin": 
        return date.strftime("%#m/%#d")
    elif platform == "darwin" or platform == "linux" or platform == "linux2":
        return date.strftime("%-m/%-d")

announce_statuses.start()
bot.run(TOKEN)