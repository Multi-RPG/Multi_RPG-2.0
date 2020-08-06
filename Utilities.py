#!/usr/bin/env python3
import discord
import asyncio
import re
from discord.ext import commands


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
                if int(args[0]) > 100:
                    await context.send("100 messages maximum!")
                    return
                deleted = await context.channel.purge(limit=int(args[0]))
                await context.send("Deleted %s message(s)" % str(len(deleted)))

            except:
                await context.channel.purge(context.message.channel, limit=1)
                await context.send(
                    "Cleared 1 message... "
                    "Use **=clear X** to clear a higher, specified amount."
                )
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
                error_msg = await context.send(context.author.mention + " No links permitted!")
                await asyncio.sleep(6)
                await error_msg.delete()
                return

            # if a negative sign in the user's time parameter...
            if "-" in time:
                error_msg = await context.send("Timer can not be negative...")
                await asyncio.sleep(10)
                await error_msg.delete()
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
                return
        # if arguments weren't passed in correctly
        except:
            error_msg = await context.send(error_str)
            await asyncio.sleep(15)
            await error_msg.delete()
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
        await context.send(context.author.mention + " **Reminder:** " + msg)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="id", aliases=["myid", "ID"])
    async def discordID(self, context):
        await context.send(f'{context.author.mention} Your discord ID: **{context.author.id}**')

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
        em.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/440598342767083521.png?size=64"
        )
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
        em.set_thumbnail(
            url="https://cdn.discordapp.com/emojis/440598342767083521.png?size=40"
        )
        await context.send(embed=em)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="serverinfo",
        description="Get server infoe",
        brief="server information",
        aliases=["si", "info", "i", "server"],
    )
    async def server_info(self, context):
        # server_name =
        # number_of_emojis =
        # number_of_members =
        # number_of_channels =
        # server_owner =
        # print(server_name)
        # print(number_of_emojis)
        # print(number_of_members)
        # print(number_of_channels)
        # print(server_owner)
        # print(type(server_owner))

        embed = discord.Embed(colour=discord.Colour(0x28D1F7))

        embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")
        embed.set_author(name="Server Information for 'Testing'")
        embed.add_field(name="Member count", value="100", inline=True)
        embed.add_field(name="User count", value="100", inline=True)
        embed.add_field(name="Bot", value="100", inline=True)
        embed.add_field(name="Role count", value="100", inline=True)
        embed.add_field(name="Text Channels", value="100", inline=True)
        embed.add_field(name="Voice Channels", value="100", inline=True)
        embed.add_field(name="Emoji Count", value="100", inline=True)
        embed.add_field(name="Owner", value="tony#1020", inline=True)
        embed.add_field(name="Nitro Booster", value="2", inline=True)
        embed.add_field(name="Server Created at", value="2020-04-12", inline=True)

        await context.send(embed=embed)


def setup(client):
    client.add_cog(Utilities(client))
