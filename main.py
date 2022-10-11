import discord
import revolt
from revolt import utils
from discord.ext import commands

import asyncio
import aiohttp
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

# discord : revolt

loop = asyncio.new_event_loop()

with open("map.json") as f:
    channelmap = json.load(f)
mapchannel = {}

for pair in channelmap.items():
    mapchannel[pair[1]] = pair[0]

revoltt, discordt = os.getenv("revolt"), os.getenv("discord")
revolts, discordg = os.getenv("revoltserver"), os.getenv("discordguild")

guild, server = None, None

bot = commands.Bot(
    command_prefix="-",
    allowed_mentions=discord.AllowedMentions(
        everyone=False,
        users=True,
        roles=True
    ),
    intents=discord.Intents.all(),
    loop=loop
)

client = None


@bot.listen()
async def on_ready():
    global guild
    print("Discord is ready")
    guild = bot.get_guild(int(discordg))


@bot.listen()
async def on_message(message):
    if message.author.id == bot.user.id:
        return
    if str(message.channel.id) in channelmap:
        print(
            f"Sending '{message.content}' to {channelmap[str(message.channel.id)]}")
        content = message.content
        a = re.match("<@([0-9]*)>", content)
        if a:
            c = discord.utils.get(
                guild.members, id=int(a.group(1)))
            content = re.sub("<@([0-9]*)>", "@" +
                             (c.nick or c.name), content)
        a = re.match("@(\S*)", content)
        if a:
            try:
                b = utils.get(server.members, nickname=a.group(1))
            except:
                b = None
            if not b:
                b = utils.get(server.members, name=a.group(1))
            if b:
                content = re.sub("@(\S)*", f"<@{b.id}>", content)
        if cc := "\n".join([attachment.url for attachment in message.attachments]):
            content += "\n" + cc
        await client.get_channel(channelmap[str(message.channel.id)]).send(f"`{message.author.nick or message.author.name}` " + content)


class Client(revolt.Client):
    async def on_ready(self, *args):
        global server, ll
        print("Revolt is ready")
        server = self.get_server(revolts)
        discord.utils.setup_logging()
        await bot.start(discordt)

    async def on_message(self, message: revolt.Message):
        if message.author.id == self.user.id:
            return
        if message.content.startswith("-invite"):
            i = await guild.system_channel.create_invite(reason="Revolt", max_age=300)
            await message.channel.send(i.url)
            return

        print(
            f"Sending '{message.content}' to {mapchannel[message.channel.id]}")
        content = message.content
        a = re.match("<@([0-9a-zA-Z]*)>", content)
        if a:
            c = utils.get(
                server.members, id=a.group(1))
            content = re.sub("<@([0-9a-zA-Z]*)>", "@" +
                             (c.nickname or c.name), content)
        a = re.match("@(\S*)", content)
        if a:
            b = discord.utils.get(guild.members, nick=a.group(1))
            if not b:
                b = discord.utils.get(guild.members, name=a.group(1))
            if b:
                content = re.sub("@(\S)*", f"<@{b.id}>", content)
        if cc := "\n".join([attachment.url for attachment in message.attachments]):
            content += "\n" + cc
        await bot.get_channel(int(mapchannel[message.channel.id])).send(f"`{message.author.nickname or message.author.name}` " + content)


async def main():
    async with aiohttp.ClientSession(loop=loop) as session:
        global client
        client = Client(session, revoltt)
        await client.start()

asyncio.set_event_loop(loop)
loop.run_until_complete(main())
