from json.decoder import JSONDecodeError
import os
import json
from datetime import date, timedelta
from discord.ext.commands.errors import MissingRequiredArgument
from dotenv import load_dotenv
from discord.ext import commands, tasks

##Setup
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('CHANNEL')
JSON_FILE = os.getenv('JSON_FILE')
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
@bot.command(name='res', help='Shows your resolution and status')
async def resolution(ctx):
    try: 
        print(log[str(ctx.author.id)])
        user_info = log[str(ctx.author.id)]
        await ctx.send(f'{user_info["mention"]}\'s resolution: {user_info["resolution"]}\n \
        Most Recent Update: {user_info["update"]} on {user_info["update_date"]}')
    except KeyError: 
        await ctx.send('You don\'t have a resolution! use !set to make one')

@bot.command(name='set', help='Sets your resolution for 2022. ex: !set "Eat Healthy"')
async def set_resolution(ctx, resolution: str):
    id = str(ctx.author.id)
    log[id] = {}
    log[id]['resolution'] = resolution
    log[id]['name'] = ctx.author.name
    log[id]['mention'] = '<@'+str(ctx.author.id)+'>'
    log[id]['update'] = ''
    log[id]['update_date'] = date.today().isoformat()
    response=resolution
    print(log[ctx.author.id])
    dump_json()
    await ctx.send(f'{ctx.author.name}\'s New Year Resolution: ' + response)

@bot.command(name='update', help='Tells everyone any updates on your resolution. ex: !updated "this is my update today"')
async def update_resolution(ctx, update: str):
    try:
        log[str(ctx.author.id)]['update'] = update
        log[str(ctx.author.id)]['update_date'] = date.today().isoformat()
        dump_json()
        await ctx.send(f'Thanks for updating us {ctx.author.name}!')
    except MissingRequiredArgument:
        await ctx.send(f'Don\'t forget to include the update ( !update "this is my update today")')

##Tasks
@tasks.loop(hours=24)
async def announce_statuses():
    if date.today().weekday() != 6:
        return
    channel = await bot.fetch_channel(int(CHANNEL))
    await channel.send(f'This week\'s resolution results: ')
    for user in log:
        if date.fromisoformat(log[user]['update_date']) > (date.today()-timedelta(days=7)):
            await channel.send(f'{log[user]["mention"]} \u2714')
        else:
            await channel.send(f'{log[user]["mention"]} \u274C')

##Helpers
def dump_json():
    json_object = json.dumps(log, indent = 4)
    with open(JSON_FILE, 'w') as outfile:
        outfile.write(json_object)

announce_statuses.start()
bot.run(TOKEN)