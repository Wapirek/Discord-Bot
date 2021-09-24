import asyncio
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

client = discord.Client()
bot = commands.Bot(command_prefix="!")

players = {}
gifs = []
queue = {}

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


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
    # status = json_dog['status']
    return (random_dog)


@bot.event
async def on_ready():
    print('online')


@bot.command()
async def pet(ctx, who: discord.Member):
    gif_update()
    await ctx.channel.purge(limit=1)
    await ctx.send(str(ctx.author.mention) + " pet " + str(who.mention) + " :heart:")
    await ctx.send(file=discord.File("gif/" + str(gifs[random.randint(0, len(gifs) - 1)])))


@bot.command()
async def gif_reload(ctx):
    gif_update()


@bot.command()
@commands.cooldown(1, 2.5)
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
async def delete(ctx, arg=None):
    await ctx.channel.purge(limit=1)
    if arg:
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
    print(ctx.message.author)


@bot.command()
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel!".format(ctx.message.author.mention))
        return
    else:
        channel = ctx.author.voice.channel
        await ctx.send(f'Connected to ``{channel}``')

    await channel.connect()

@bot.command()
async def leave(ctx):
    print(ctx.voice_client)
    if ctx.voice_client:  # If the bot is in a voice channel
        await ctx.guild.voice_client.disconnect()  # Leave the channel
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command()
async def play(ctx, *, url):
    try:
        if not ctx.voice_client:
            await join(ctx)
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            print(queue)

            if len(queue) == 0:
                print('len == 0')
                start_playing(ctx.voice_client, filename)
                await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n:musical_note: **Now '
                                                                           'Playing:** ``{}'.format(filename.title) + "``")
            else:
                print('len else')
                queue[len(queue)] = filename
                await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n:musical_note: **Added'
                                                                           ' to queue:** ``{}'.format(filename.title) + "``")

    except discord.errors.ClientException:
        await ctx.send("The bot is already playing audio...")

#todo queue naprawić bo nie działa

def start_playing(voice_client, filename):
    print(filename)
    queue[0] = filename

    i = 0
    while i < len(queue):
        try:
            voice_client.play(queue[i], after=lambda e: print('error: %s' % e) if e else None)
        except:
            pass
        i += 1


@bot.command()
async def q(ctx):
    await ctx.send(queue)


@bot.command()
async def ffff(ctx):
    await ctx.message.guild.voice_client.play


@bot.command()
async def stop(ctx):
    ctx.voice_client.stop()


@bot.command()
async def pause(ctx):
    voice = ctx.voice_client
    if voice.is_playing():
        voice.pause()
        user = ctx.message.author.mention
        await ctx.send(f"Bot was paused by {user}")
    else:
        await ctx.send("Currently no audio is playing.")


@bot.command()
async def resume(ctx):
    voice = ctx.voice_client
    if voice.is_paused():
        voice.resume()
        user = ctx.message.author.mention
        await ctx.send(f"Bot was resumed by {user}")
    else:
        await ctx.send("The audio is not paused.")

bot.run(os.getenv('TOKEN'))
