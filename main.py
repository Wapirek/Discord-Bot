import asyncio
import os
import datetime
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
from tinytag import TinyTag



load_dotenv()

client = discord.Client()
bot = commands.Bot(command_prefix="!")

gifs = []
queue = []

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    'outtmpl': '%(title)s.mp3',
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


class Song:
    def __init__(self, filename):
        self.filename = filename
        self.time = datetime.timedelta(seconds=filename.data['duration'])


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
    return random_dog


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
async def gif_reload():
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
    embed_var = discord.Embed(title="Currently playing:", color=0x00ff00)
    embed_var.add_field(name="1. Piosenka 1", value="_ _", inline=False)
    embed_var.add_field(name="2. Piosenka 2", value="_ _", inline=False)
    await ctx.send(embed=embed_var)


@bot.command()
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} u must join a voice channel first!".format(ctx.message.author.mention))
    else:
        channel = ctx.author.voice.channel
        await ctx.send(f'Joining ``{channel}``')
        await channel.connect()


@bot.command()
async def leave(ctx):
    print(ctx.voice_client)
    if ctx.voice_client:  # If the bot is in a voice channel
        await ctx.guild.voice_client.disconnect()  # Leave the channel
    else:
        await ctx.send("Not currently in a channel.")


@bot.command(pass_context=True)
async def play(ctx, *, url):
    try:
        if not ctx.voice_client:
            await join(ctx)
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            if len(queue) == 0:
                print('len == 0')
                queue.append(Song(filename))
                print(queue)
                start_playing(ctx)
                if url.startswith("https://") or url.startswith("http://"):
                    await ctx.send(':musical_note: **Now Playing:** ``{}'.format(filename.title) + "``")
                else:
                    await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n:musical_note: **Now '
                                                                               'Playing:** ``{}'.format(filename.title) + "``")
            else:
                queue.append(Song(filename))
                print(queue)
                if url.startswith("https://") or url.startswith("http://"):
                    await ctx.send(':musical_note: **Added to queue:** ``{}'.format(filename.title) + "``")
                else:
                    await ctx.send(f':mag_right: **Searching for** ``' + url + '``\n:musical_note: **Added'
                                                                               ' to queue:** ``{}'.format(filename.title) + "``")
    except discord.errors.ClientException:
        pass
    except discord.ext.commands.errors.MissingRequiredArgument:
        await ctx.send("The player is not currently playing anything.\n"
                       "Use ``!play <url-or-search-terms>`` to add a song.")


def start_playing(ctx):
    print('poczatek grania')
    player = ctx.voice_client

    ctx.voice_client.play(queue[0].filename, after=lambda a: next_song(ctx))


def next_song(ctx):
    if len(queue) > 1:
        queue.pop(0)
        start_playing(ctx)
    else:
        queue.pop(0)
        ctx.voice_client.stop()


@bot.command()
async def stop(ctx):
    if not len(queue) == 0:
        ctx.voice_client.stop()
        await ctx.send("The queue has been emptied, ``{}`` tracks have been removed.".format(len(queue)))
        queue.clear()
    else:
        await ctx.send("Not currently playing anything.")

@bot.command()
async def q(ctx):
    if not queue:
        await ctx.send('Not currently playing anything.')
    else:
        i = 1
        embed_var = discord.Embed(title="Currently playing:", color=0x19a56f)
        for song in queue:
            embed_var.add_field(name=str(i) + '. ' + song.filename.title, value=song.time, inline=False)
            i += 1
        await ctx.send(embed=embed_var)


@bot.command()
async def pause(ctx):
    voice = ctx.voice_client
    if voice.is_playing():
        voice.pause()
        await ctx.send(f"The player is now paused. You can resume it with ``!resume``")
    else:
        await ctx.send("The player is not currently playing anything.\n"
                       "Use ``!play <url-or-search-terms>`` to add a song.")


@bot.command()
async def skip(ctx):
    ctx.voice_client.stop()
    ctx.send("Skipped!")


@bot.command()
async def remove(ctx, id):
    id = int(id) - 1
    await ctx.send("`{}` has been removed from queue.".format(queue[id].filename.title))
    if id == 0:
        ctx.voice_client.stop()
    else:
        queue.pop(id)


@bot.command()
async def resume(ctx):
    voice = ctx.voice_client
    if voice.is_paused():
        voice.resume()
        await ctx.send("The player is now unpaused.")
    else:
        await ctx.send("The player is not paused.")



bot.run(os.getenv('TOKEN'))
