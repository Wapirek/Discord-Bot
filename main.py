import os
import discord
import json
import requests
import io
import aiohttp
import time
import youtube_dl
from discord.ext import commands


# client = discord.Client()
bot = commands.Bot(command_prefix='!')

players = {}


def dog_url():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    json_dog = json.loads(response.text)
    random_dog = json_dog['message']
    #status = json_dog['status']
    return (random_dog)


@bot.event
async def on_ready():
    print('online')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('test'):
        await message.channel.send('TEST!!!')

    if message.content.startswith('!pjeski') or message.content.startswith('!pjesek'):
        print('pjesek requested')
        async with aiohttp.ClientSession() as session:
            async with session.get(dog_url()) as resp:
                if resp.status != 200:
                    return await message.channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await message.channel.send(file=discord.File(data, 'dog.png'))

    if message.content.startswith('!delete'):
        await message.channel.purge(limit=1)
        await message.channel.send('Usunięto!')
        time.sleep(3)
        await message.channel.purge(limit=1)


@bot.command()
async def test(ctx):
    print("xd")
    await bot.user.channel.send('TEST!!!')
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




bot.run('Njc0NzYwMjc2MzIyNTQ5NzYx.XjtReg.gAw3FcO8uqhMbAldvSTogeSw8QY')
