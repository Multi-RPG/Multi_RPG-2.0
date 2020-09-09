#!/usr/bin/env python3
import discord
import asyncio
import re
import logging

from discord.ext import commands

log = logging.getLogger("MULTI_RPG")


class Utilities(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 25, commands.BucketType.user)
    @commands.command(
        name="clear",
        description="Deletes messages in the channel.",
        brief='can use "=clear" or "=clear X", with X being #  messages to delete',
        aliases=["c", "clr", "CLEAR", "C", "CLR", "clean", "CLEAN"],
    )
    async def clear(self, context, *args):
        # if the user has admin privileges, permit them to use this command
        if context.author.guild_permissions.administrator:
            # try-catch block, because of *args array.
            # if no argument given in discord after "=clear", it will go to the exception
            try:
                if args:
                    if int(args[0]) > 100:
                        await context.send("100 messages maximum!")
                        return
                    deleted = await context.channel.purge(limit=int(args[0]))
                    await context.send(f"Deleted {len(deleted)} message(s)")
                else:
                    await context.channel.purge(limit=1)
                    await context.send("Cleared 1 message... " "Use **=clear X** to clear a higher, specified amount.")
            except Exception as e:
                msg = f"Not ok! {e.__class__} occurred"
                log.debug(msg)
        # else inform the user they lack sufficient privileges
        else:
            await context.send("You need to be a local server administrator to do that!")

    @commands.cooldown(1, 6, commands.BucketType.user)
    @commands.command(
        name="remind",
        description="Reminds you by timer.",
        brief='=remindme "message" X',
        aliases=["remindme", "ALARM", "timer", "alarm,", "REMIND", "REMINDME"],
    )
    async def remindme(self, context, *args):
        error_str = '```ml\nUse =remindme "message" X     -- X being timer (Ex: 20s, 50m, 3hr)```'
        msg = ""
        unit = ""

        # try to process the arguments
        try:
            # if the command was processed with iphone mobile quotes “ ”
            if "“" or "”" in args:
                # compile all arguments together, (except the last one, which will be time)
                for argument in args[0 : len(args) - 1]:
                    msg = msg + argument + " "
                # strip mobile's weird double quotes from the new string
                msg = str(msg.replace("“", "").replace("”", ""))
                # the last argument will be time
                time = args[len(args) - 1]
            # else no iphone quotation marks found, proceed as normal
            else:
                msg = str(args[0])
                time = args[1]

            # prevent users from using @everyone or @here tag to exploit the bot to tag those groups in the message
            if "@everyone" in msg:
                msg = str(msg.replace("@everyone", "Everyone!"))
            if "@here" in msg:
                msg = str(msg.replace("@here", "Here!"))
            # prevent users from using links in remindme's message
            if "http" in msg:
                error_msg = await context.send(f"{context.author.mention} No links permitted!")
                await asyncio.sleep(6)
                await error_msg.delete()
                await context.message.delete()
                return

            # if a negative sign in the user's time parameter...
            if "-" in time:
                error_msg = await context.send("Timer can not be negative...")
                await asyncio.sleep(10)
                await error_msg.delete()
                await context.message.delete()
                return
            # if "s" in their time parameter, simply set seconds to "s" after retrieving the integer
            if "s" in time:
                unit = "second(s)"
                time = int(re.findall(r"\d+", time)[0])
                seconds = 1 * time
            # if "m" in their time parameter, set seconds to 60 * parameter after retrieving the integer
            elif "m" in time:
                unit = "minute(s)"
                time = int(re.findall(r"\d+", time)[0])
                seconds = 60 * time
            # if "h" in their time parameter, set seconds to 3600 * parameter after retrieving the integer
            elif "h" in time:
                unit = "hour(s)"
                time = int(re.findall(r"\d+", time)[0])
                seconds = 3600 * time
            # if none of the above units of time were found, send an error message
            else:
                error_msg = await context.send("Use a **valid** unit of time (Ex: _20s_, _50m_, _3hr_)")
                await asyncio.sleep(15)
                await error_msg.delete()
                await context.message.delete()
                return
        # if arguments weren't passed in correctly
        except:
            error_msg = await context.send(error_str)
            await asyncio.sleep(15)
            await error_msg.delete()
            await context.message.delete()
            return

        # embed the link, set thumbnail, send reminder confirmation, then wait X seconds
        em = discord.Embed(
            title="Remindme registered",
            description="Will remind you in {} {}".format(time, unit),
            colour=0x607D4A,
        )
        em.set_thumbnail(url="https://i.imgur.com/1HdQNaz.gif")
        await context.send(embed=em)

        await asyncio.sleep(seconds)
        await context.send(f"{context.author.mention} **Reminder:** {msg}")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="id", aliases=["myid", "ID"])
    async def discordID(self, context):
        await context.send(f"{context.author.mention} Your discord ID: **{context.author.id}**")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="code",
        description="Give link to code",
        brief='can use "=code',
        aliases=["CODE"],
    )
    async def source_code_link(self, context):
        # embed the link, set thumbnail and send
        em = discord.Embed(
            title="Source code link",
            description="https://github.com/Multi-RPG/Multi_RPG-2.0",
            colour=0x607D4A,
        )
        em.set_thumbnail(url="https://i.imgur.com/nbTu5lX.png")
        await context.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="invite",
        description="Give link to code",
        brief='can use "=code',
        aliases=["link", "botlink", "invitelink", "INVITE"],
    )
    async def invite_link(self, context):
        # embed the link, set thumbnail and send
        em = discord.Embed(
            title="Bot invite link",
            description="https://discordapp.com/oauth2/authorize?client_id=486349031224639488&permissions=8&scope=bot",
            colour=0x607D4A,
        )
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/440598342767083521.png?size=64")
        await context.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="vote",
        description="Give link to vote for bot",
        brief='can use "=code',
        aliases=["VOTE", "votelink", "VOTELINK"],
    )
    async def vote_link(self, context):
        # embed the link, set thumbnail and send
        em = discord.Embed(
            title="Vote link",
            description="https://discordbots.org/bot/486349031224639488/vote",
            colour=0x607D4A,
        )
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/440598342767083521.png?size=40")
        await context.send(embed=em)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(
        name="serverinfo",
        description="Get server information.",
        brief="server info",
        aliases=["si", "info", "i", "server", "guild", "guildinfo", "gi"],
    )
    async def server_info(self, context):
        server_name = context.guild.name
        title = f"Server Information for {server_name}"
        number_of_emojis = len(context.guild.emojis)

        # Using Guild.members here instead of Guild.member_count,
        # because we need to filter the bots out of the counting.
        number_of_members = 0
        for member in context.guild.members:
            # If it's a bot we skip it.
            if member.bot:
                continue
            number_of_members += 1

        number_of_voicechannels = len(context.guild.voice_channels)
        number_of_textchannels = len(context.guild.text_channels)
        number_of_roles = len(context.guild.roles)
        guild_owner = context.guild.owner
        guild_booster_level = context.guild.premium_tier
        number_of_boosters = context.guild.premium_subscription_count
        guild_region = str(context.guild.region)
        guild_create_at = context.guild.created_at.strftime("%b %d %Y %H:%M:%S")

        embed = discord.Embed(colour=discord.Colour(0x28D1F7))
        embed.set_thumbnail(url=context.guild.icon_url)
        embed.set_author(name=title)
        embed.add_field(name="Member Count", value=number_of_members, inline=True)
        embed.add_field(name="Role Count", value=number_of_roles, inline=True)
        embed.add_field(name="Emoji Count", value=number_of_emojis, inline=True)
        embed.add_field(name="VoiceChannel Count", value=number_of_voicechannels, inline=True)
        embed.add_field(name="TextChannel Count", value=number_of_textchannels, inline=True)
        embed.add_field(name="Server Owner", value=guild_owner, inline=True)
        embed.add_field(name="Server Booster Level", value=guild_booster_level, inline=True)
        embed.add_field(name="Server Booster Count", value=number_of_boosters, inline=True)
        embed.add_field(name="Region", value=guild_region, inline=True)
        embed.add_field(name="Server Created at", value=guild_create_at, inline=True)

        await context.send(embed=embed)
        await context.message.delete()


def setup(client):
    client.add_cog(Utilities(client))
