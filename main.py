import os
import discord
import json
import requests
import io
import aiohttp
import time
import random
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

#client = discord.Client()
bot = commands.Bot(command_prefix="!")



players = {}
gifs = []

def gif_update():
    gifs.clear()
    files = os.listdir('./gif')
    for file in files:
        gifs.append(file)
        print(file)


def dog_url():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    json_dog = json.loads(response.text)
    random_dog = json_dog['message']
    #status = json_dog['status']
    return (random_dog)


@bot.event
async def on_ready():
    print('online')

@bot.command()
async def pet(ctx,who: discord.Member):
    gif_update()
    await ctx.channel.purge(limit=1)
    await ctx.send(str(ctx.author.mention) + " pet " +str(who.mention)+" :heart:")
    await ctx.send(file=discord.File("gif/"+str(gifs[random.randint(0,len(gifs)-1)])))

@bot.command()
async def gif_reload(ctx):
    gif_update()

@bot.command()
@commands.cooldown(1,2.5)
async def pjesek(ctx):
    print('pjesek requested')
    async with aiohttp.ClientSession() as session:
        async with session.get(dog_url()) as resp:
            if resp.status != 200:
                return await ctx.send('Could not download file...')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'dog.png'))

@bot.command()
async def pjeski(ctx):
    await pjesek(ctx)


@bot.command()
@commands.has_any_role('ogul sie', 'Dziadu ak Head Admin')
async def delete(ctx,arg=None):
    await ctx.channel.purge(limit=1)
    if (arg != None):
        await ctx.channel.purge(limit=int(arg))
    else:
        await ctx.channel.purge(limit=1)
    await ctx.send('Usunięto!')
    time.sleep(1)
    await ctx.channel.purge(limit=1)


@bot.command()
async def pisz(ctx):
    for a in range(5):
        await ctx.send(a)

@bot.command()
async def test(ctx):
    print("xd")
    await ctx.send('TEST!!!')

@bot.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()


@bot.command()
async def play(ctx, url : str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Wait for the current playing music to end or use the 'stop' command")
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='Grańsko')
    await voiceChannel.connect()
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("../Discord - Tonari/"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))

bot.run(os.getenv('TOKEN'))

