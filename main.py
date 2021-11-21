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
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor
from discord.ext import commands
from dotenv import load_dotenv

# import youtube_dl

load_dotenv()
extension = ""

command_prefix = "!"
bot = commands.Bot(command_prefix=command_prefix)

time_left = 0.0
time_last_song = 0.0
t0 = 0
t1 = 0

gifs = []
queue = []

queue_msg = ""
current_last_showing_track = 0

# youtube_dl.utils.bug_reports_message = lambda: ""
ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "outtmpl": "%(title)s.mp3",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ffmpeg_options = {"options": "-vn"}

ydl = yt_dlp.YoutubeDL(ydl_opts)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.id = data.get("id")
        self.channel = data.get("uploader")
        self.url = f"https://www.youtube.com/watch?v={self.id}"
        self.time = datetime.timedelta(seconds=data.get("duration"))

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ydl.extract_info(url, download=not stream)
        )
        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]
        filename = data["url"] if stream else ydl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Song:
    def __init__(self, filename, ctx):
        self.filename = filename
        self.time = filename.time
        self.url = filename.url
        self.channel = filename.channel
        self.req = ctx.author


def gif_update():
    gifs.clear()
    api_key = os.getenv("API_KEY")
    search = "pat"
    r = requests.get(f"https://g.tenor.com/v1/search?key={api_key}&q={search}")
    json_gifs = json.loads(r.text)
    for item in json_gifs["results"]:
        gifs.append(item["media"][0]["gif"]["url"])


def dog_url():
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    json_dog = json.loads(response.text)
    random_dog = json_dog["message"]
    # status = json_dog['status']
    return random_dog


@bot.event
async def on_ready():
    gif_update()
    print("online")


# @bot.command()
# async def pet(ctx, who: discord.Member):
#     gif_update()
#     await ctx.channel.purge(limit=1)
#     await ctx.send(f"{ctx.author.mention} pet {who.mention} :heart:")
#     await ctx.send(file=discord.File(f"gif/{str(random.choice(gifs))}"))


@bot.command()
async def pet(ctx, who: discord.Member):
    gif_url = random.choice(gifs)
    print(gif_url)

    async with aiohttp.ClientSession() as session:
        async with session.get(gif_url) as resp:
            if resp.status != 200:
                return await ctx.send("Could not download file...")
            data = io.BytesIO(await resp.read())
            await ctx.send(f"{ctx.author.mention} pet {who.mention} :heart:")
            await ctx.send(file=discord.File(data, "gif.gif"))


@bot.command(aliases=["pjeski", "pjes"])
@commands.cooldown(1, 2.5)
async def pjesek(ctx):
    print("pjesek requested")
    async with aiohttp.ClientSession() as session:
        async with session.get(dog_url()) as resp:
            if resp.status != 200:
                return await ctx.send("Could not download file...")
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, "dog.png"))


@bot.command()
@commands.has_any_role("ogul sie", "Dziadu ak Head Admin")
async def delete(ctx, arg=None):
    await ctx.channel.purge(limit=1)
    if arg:
        await ctx.channel.purge(limit=int(arg))
    else:
        await ctx.channel.purge(limit=1)
    await ctx.send("Usunięto!")
    time.sleep(1)
    await ctx.channel.purge(limit=1)


@bot.command()
async def pisz(ctx):
    for a in range(5):
        await ctx.send(a)


@bot.command()
@commands.has_any_role("ogul sie", "Dziadu ak Head Admin")
async def test(ctx):
    #     for channel_name in range(22):
    #         existing_channel = discord.utils.get(ctx.guild.channels, name=str(channel_name))
    #         if existing_channel is not None:
    #             await existing_channel.delete()
    # for names in range(100):
    #     await discord.TextChannel.delete(names)
    message = await ctx.send("siema")
    # emoji = "\N{THUMBS UP SIGN}"
    await message.add_reaction(":slight_smile:")


@bot.command()
@commands.has_any_role("ogul sie", "Dziadu ak Head Admin")
async def bug(ctx):
    # user = ctx.author
    # await ctx.send("```Please explain the bug```")
    # response_description = await bot.wait_for(
    #     "message", check=lambda message: message.author == ctx.author, timeout=300
    # )
    # description = response_description.content
    # print(description)
    global reaction_message
    emojis = ["⬅️", "➡️"]

    embed = discord.Embed(title="Tile", description="Desc", color=0x00FF00)
    embed.add_field(name="Fiel1", value="hi", inline=False)
    embed.add_field(name="Field2", value="hi2", inline=False)

    reaction_message = await ctx.send(embed=embed)

    for emoji in emojis:
        await reaction_message.add_reaction(emoji)


@bot.command()
@commands.has_any_role("ogul sie", "Dziadu ak Head Admin")
async def channel(ctx):
    print(bot.get_channel(865397493599436830).id)


@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send(f"{ctx.author.mention} u must join a voice channel first!")
    else:
        channel = ctx.author.voice.channel
        await ctx.send(f"Joining {channel.mention}")
        await channel.connect()


@bot.command()
async def leave(ctx):
    print(ctx.voice_client)
    if ctx.voice_client:  # If the bot is in a voice channel
        await ctx.guild.voice_client.disconnect()  # Leave the channel
    else:
        await ctx.send("Not currently in a channel.")


# todo wychodzenie po 5 min jak nic nie gra
@bot.command(pass_context=True, aliases=["plya", "p"])
async def play(ctx, *, url):
    try:
        print(ctx.message.author)
        if not ctx.message.author.voice:
            await ctx.send(
                f"{ctx.message.author.mention} u must join a voice channel first!"
            )
            return
        if not ctx.voice_client:
            await join(ctx)
        async with ctx.typing():
            await ctx.send(f":musical_note: **Searching** :mag_right: `{url}`")
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            queue.append(Song(filename, ctx))

            if len(queue) == 1:
                time_until_play = "Now"
            else:
                global t1
                time_until_play = datetime.timedelta(0)
                t1 = time.time()
                seconds = round(t1 - t0)
                time_left_current = queue[0].time - datetime.timedelta(seconds=seconds)
                for song in queue[1:-1]:
                    time_until_play += song.time
                    print(song.time)
                time_until_play += time_left_current

            embed = discord.Embed(
                colour=0x19A56F,
                url="https://discordapp.com",
                description=f"[{filename.title}]({filename.url})",
            )
            embed.set_thumbnail(
                url=f"https://img.youtube.com/vi/{filename.id}/maxresdefault.jpg"
            )
            embed.set_author(
                name="Added to queue",
                url="https://github.com/Wapirek/Discord-Tonari",
                icon_url=f"{ctx.author.avatar_url}",
            )
            embed.add_field(name="Channel", value=f"{filename.channel}", inline=True)
            embed.add_field(name="Song Duration", value=f"{filename.time}", inline=True)
            embed.add_field(
                name="Estimated time until playing",
                value=f"{time_until_play}",
                inline=True,
            )
            embed.add_field(
                name="Position in queue", value=f"{len(queue) - 1}", inline=False
            )
            await ctx.send(content=None, embed=embed)

            start_playing(ctx)

    except discord.errors.ClientException:
        print("disc Client exception")
        pass
    except discord.ext.commands.errors.MissingRequiredArgument:
        await ctx.send(
            "The player is not currently playing anything.\n"
            "Use ``{command_prefix}play <url-or-search-terms>`` to add a song."
        )


def start_playing(ctx) -> None:
    """Take first item from queue and start playing it and"""
    global t0
    print("poczatek grania")
    ctx.voice_client.play(queue[0].filename, after=lambda a: next_song(ctx))
    t0 = time.time()


def next_song(ctx):
    if len(queue) > 1:
        queue.pop(0)
        start_playing(ctx)
    else:
        try:
            queue.pop(0)
            ctx.voice_client.stop()
        except IndexError:
            pass


@bot.command()
async def stop(ctx):
    if not len(queue) == 0:
        await ctx.send(
            f"The queue has been emptied, ``{len(queue)}`` tracks have been removed."
        )
        queue.clear()
        ctx.voice_client.stop()
    else:
        await ctx.send("Not currently playing anything.")


# todo queue zawijanie po 5 + menu reakcjowe
@bot.command(aliases=["queue"])
async def q(ctx):
    if not queue:
        await ctx.send("Not currently playing anything.")
    else:
        global current_last_showing_track
        global t1
        global queue_msg
        global time_left

        more = False

        t1 = time.time()
        seconds = t1 - t0
        time_left = queue[0].time - datetime.timedelta(seconds=(round(seconds)))

        embed = discord.Embed(
            colour=discord.Colour(0xFD05C2),
            description=f"**[Queue for {ctx.guild}](https://google.com)**",
        )
        embed.add_field(
            name="__Now Playing:__",
            value=f"[{queue[0].filename.title}]({queue[0].url}) | `{time_left} Requested by: {queue[0].req}`",
            inline=False,
        )
        if len(queue) > 1:
            i = 2
            embed.add_field(
                name="__Up Next:__",
                value=f"`1.` [{queue[1].filename.title}]({queue[1].url}) | `{queue[1].time} Requested by: {queue[1].req}`",
                inline=False,
            )
            for song in queue[i : i + 4]:
                embed.add_field(
                    name="\u200b",
                    value=f"`{str(i)}.` [{queue[i].filename.title}]({queue[i].url}) | `{queue[i].time} Requested by: {queue[i].req}`",
                    inline=False,
                )
                current_last_showing_track = i
                i += 1
            if len(queue) > 6:
                more = True
                embed.add_field(
                    name="\u200b",
                    value=f"**and `{len(queue)-6}` more**",
                    inline=False,
                )

        queue_msg = await ctx.send(embed=embed)
        print(current_last_showing_track)

        if more:
            emojis = ["⬅️", "➡️"]
            for emoji in emojis:
                await queue_msg.add_reaction(emoji)


def prev_embed(ctx):
    return embed


def next_embed(ctx):
    global current_last_showing_track
    i = current_last_showing_track + 1

    if i > len(queue):
        return

    embed = discord.Embed(
        colour=discord.Colour(0xFD05C2),
        description=f"**[Queue for {ctx.guild}](https://google.com)**",
    )
    embed.add_field(
        name="__Now Playing:__",
        value=f"[{queue[0].filename.title}]({queue[0].url}) | `{time_left} Requested by: {queue[0].req}`",
        inline=False,
    )
    for song in queue[i : i + 5]:
        embed.add_field(
            name="\u200b",
            value=f"`{str(i)}.` [{queue[i].filename.title}]({queue[i].url}) | `{queue[i].time} Requested by: {queue[i].req}`",
            inline=True,
        )
        current_last_showing_track = i
        i += 1

    return embed


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    global reaction_message
    emoji = reaction.emoji

    if reaction.message == queue_msg:
        if emoji == "⬅️":
            await reaction.remove(user)
            await reaction.message.edit(embed=prev_embed(reaction.message))
        elif emoji == "➡️":
            await reaction.remove(user)
            await reaction.message.channel.send(embed=next_embed(reaction.message))

    # adminBug = bot.get_channel(890002939022815262)
    # message = await adminBug.send(embed=embed)

    print(emoji)


@bot.command()
async def pause(ctx):
    try:
        voice = ctx.voice_client
        if voice.is_playing():
            voice.pause()
            await ctx.send(
                f"The player is now paused. You can resume it with ``{command_prefix}resume``"
            )
        else:
            await ctx.send(
                "The player is not currently playing anything.\n"
                f"Use ``{command_prefix}play <url-or-search-terms>`` to add a song."
            )
    except AttributeError:
        await ctx.send(
            "The player is not currently connected to any channel.\n"
            f"Use ``{command_prefix}play <url-or-search-terms>`` to add a song.\n"
            f"Use ``{command_prefix}join`` to join to the channel."
        )


@bot.command()
async def skip(ctx):
    ctx.voice_client.stop()
    await ctx.send("Skipped!")


@bot.command()
async def remove(ctx, id):
    id = int(id)
    if id > 0:
        await ctx.send(
            "`{}` has been removed from queue.".format(queue[id].filename.title)
        )
        queue.pop(id)


@bot.command()
async def resume(ctx):
    voice = ctx.voice_client
    if voice.is_paused():
        voice.resume()
        await ctx.send("The player is now unpaused.")
    else:
        await ctx.send("The player is not paused.")


def waifu_url(tag, typ, gif):
    response = requests.get(f"https://api.waifu.im/{typ}/{tag}/?gif={gif}")
    json_w = json.loads(response.text)
    print(json_w)
    if json_w["code"] == 404:
        random_w = "error"
    else:
        random_w = json_w["tags"][0]["images"][0]["url"]
        global extension
        extension = json_w["tags"][0]["images"][0]["extension"]
    print(random_w)
    return random_w


@bot.command()
async def waifu(ctx, tag="waifu", gif=None):
    if tag == "help":
        embed = discord.Embed(title="Available tags:", colour=discord.Colour(0xBD10E0))
        embed.add_field(name="SFW:", value="`all`\n`maid`", inline=False)
        embed.add_field(
            name="NSFW:",
            value="`ass`\n`ecchi`\n`ero`\n`hentai`\n`maid_nsfw`\n`milf`",
            inline=True,
        )
        embed.add_field(
            name="_ _",
            value="`oppai`\n`oral`\n`paizuri`\n`selfies`\n`uniform`",
            inline=True,
        )
        await ctx.send(embed=embed)
        return

    gif = "True" if gif else "False"

    typ = "nsfw"
    if tag == "maid" or tag == "waifu" or tag == "all":
        typ = "sfw"
    if tag == "maid_nsfw":
        tag = "maid"

    if typ == "nsfw" and not ctx.channel.is_nsfw():
        await ctx.send(f"{ctx.channel.mention} is not tagged as NSFW!")
        return

    url = waifu_url(tag, typ, gif)
    if url == "error":
        await ctx.send(
            f"Sorry there is no image matching your criteria with the tag : {tag}. Please change the "
            f"criteria or consider changing your tag."
        )
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("Could not download file...")
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, f"waifu{extension}"))
            print("send waifu")


# todo przy mergowaniu do main zmienić
#bot.run(os.getenv("TOKEN_DEV"))
bot.run(os.getenv('TOKEN'))
