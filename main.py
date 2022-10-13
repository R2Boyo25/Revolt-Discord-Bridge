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
import logging

load_dotenv()

# discord : revolt

loop = asyncio.new_event_loop()

with open("map.json") as f:
    channelmap: "Discord -> Revolt" = json.load(f)
mapchannel: "Revolt -> Discord" = {}

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

    # Discord -> Revolt
    if str(message.channel.id) in channelmap:
        if int(message.author.discriminator) == 0:
            return

        content = message.content

        def repl(match):
            c = discord.utils.get(
                guild.members, id=int(match.group(1)))

            if not c:
                return match.group()

            return "@" + (c.nick or c.name)

        content = re.sub("<@([0-9]*)>", repl, content)

        def repl(match):
            try:
                return f"{utils.get(server.members, nickname=match.group(1)).id}>"
            except:
                try:
                    return f"<@{utils.get(server.members, name=match.group(1)).id}>"
                except:
                    return match.group()

        content = re.sub("@(\S*)", repl, content)

        if cc := "\n".join([attachment.url for attachment in message.attachments]):
            content += "\n" + cc

        print(
            f"Sending '{message.content}' to {channelmap[str(message.channel.id)]}")

        try:
            masquerade = revolt.Masquerade(
                name=(message.author.nick or message.author.name), avatar=message.author.avatar.url)

            await client.get_channel(channelmap[str(message.channel.id)]).send(content, masquerade=masquerade)

        except:
            content = f"`{message.author.display_name or message.author.name}` " + content

            await client.get_channel(channelmap[str(message.channel.id)]).send(content)


class Client(revolt.Client):
    async def on_ready(self, *args):
        global server, ll
        print("Revolt is ready")
        server = self.get_server(revolts)
        discord.utils.setup_logging(level=logging.WARNING)
        await bot.start(discordt)

    async def on_message(self, message: revolt.Message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith("-invite"):
            i = await guild.system_channel.create_invite(reason="Revolt", max_age=300)
            await message.channel.send(i.url)
            return

        # Revolt -> Discord
        if message.channel.id in mapchannel:
            content = message.content

            def repl(match):
                try:
                    c = utils.get(server.members, id=match.group(1))

                    return "@" + (c.nickname or c.name)

                except:
                    return match.group()

            content = re.sub("<@([0-9a-zA-Z]*)>", repl, content)

            def repl(match):
                b = discord.utils.get(guild.members, nick=match.group(1))

                if not b:
                    b = discord.utils.get(guild.members, name=match.group(1))

                if not b:
                    return match.group()

                return f"<@{b.id}>"

            content = re.sub("@(\S*)", repl, content)

            if cc := "\n".join([attachment.url for attachment in message.attachments]):
                content += "\n" + cc

            print(
                f"Sending '{message.content}' to {mapchannel[message.channel.id]}")

            try:

                channel = bot.get_channel(int(mapchannel[message.channel.id]))

                for _webhook in await channel.webhooks():
                    if _webhook.name == "RevoltBridge":
                        webhook = _webhook
                else:
                    webhook = await channel.create_webhook(name="RevoltBridge")

                await webhook.send(
                    content, username=message.author.nickname or message.author.name, avatar_url=message.author.avatar.url)

            except:

                content = f"`{message.author.nickname or message.author.name}` " + content

                await bot.get_channel(int(mapchannel[message.channel.id])).send(content)


async def main():
    async with aiohttp.ClientSession(loop=loop) as session:
        global client
        client = Client(session, revoltt)
        await client.start()

asyncio.set_event_loop(loop)
loop.run_until_complete(main())
