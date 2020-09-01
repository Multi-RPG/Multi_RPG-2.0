#!/usr/bin/env python3
import re
import discord
import asyncio
import logging

from discord.ext import commands
from DiscordBotsOrgApi import DiscordBotsOrgAPI
from Users import Users

log = logging.getLogger("MULTI_RPG")


# short decorator function declaration, confirm that command user has an account in database
def has_account():
    def predicate(ctx):
        user = Users(ctx.message.author.id)
        if user.find_user() == 0:
            return False
        else:
            return True

    return commands.check(predicate)


# short decorator function declaration, confirm that command user has voted for the bot on discordbots.org
def has_voted():
    def predicate(ctx):
        # create object of discordbotsapi to make use of the api
        checker = DiscordBotsOrgAPI()
        # check if the user attempting to use this command has voted for the bot within 24 hours
        # if they have not voted recently, let the error handler in Main.py give the proper error message
        if checker.check_upvote(ctx.author.id) == 0:
            return False
        else:
            return True

    return commands.check(predicate)


class Account(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="create", description="make a user", brief="start a user account", aliases=["register"],
    )
    async def register(self, context):
        # create new user instance with their discord ID to store in database
        new_user = Users(context.author.id)

        if new_user.find_user() == 1:
            await context.send("<:worrymag1:531214786646507540> You **already** have an account registered!")
            return

        em = discord.Embed(title="", colour=0x607D4A)
        em.add_field(
            name=context.author.display_name, value=new_user.add_user(), inline=True,
        )
        em.set_thumbnail(url=context.author.avatar_url)
        await context.send(embed=em)

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="money", aliases=["m", "MONEY"])
    async def money(self, context, *args):
        try:
            # using money on a target.
            if len(args) > 0:
                # use regex to extract only numbers to get their discord ID,
                # ex: <@348195501025394688> to 348195501025394688
                # create user instance with their target's discord ID, check database for their money field
                target_id = re.findall(r"\d+", args[0])[0]
                target = Users(target_id)
                if target.find_user() == 0:
                    await context.send("Target does not have account.")
                    return

                # fetch_user returns a User object that matches an id provided
                discord_member_target = await self.client.fetch_user(target_id)

                # embed the money retrieved from get_user_money(), set thumbnail to 64x64 version of target's id
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=discord_member_target.display_name,
                    value=f"**:moneybag: ** {target.get_user_money()}",
                    inline=True,
                )
                thumb_url = (
                    f"https://cdn.discordapp.com/avatars/{discord_member_target.id}"
                    f"/{discord_member_target.avatar}.webp?size=64"
                )

                em.set_thumbnail(url=thumb_url)

                await context.send(context.author.mention, embed=em)

            # if they passed no parameter, get their own money
            else:
                # create user instance with their discord ID, check database for their money field
                user = Users(context.author.id)

                # embed the money retrieved from get_user_money(), set thumbnail to 64x64 version of user's id
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=context.author.display_name, value=f"**:moneybag: ** {user.get_user_money()}", inline=True,
                )
                thumb_url = (
                    f"https://cdn.discordapp.com/avatars/{context.author.id}" f"/{context.author.avatar}.webp?size=64"
                )
                em.set_thumbnail(url=thumb_url)

                await context.send(context.author.mention, embed=em)

        # Added this exception for debugging purposes.
        except Exception as e:
            msg = f"Not ok! {e.__class__} occurred"
            log.debug(msg)
            await context.send(f"{context.author.mention}```ml\nuse =money like so: **=money** or **=money @user**")
        finally:
            # delete original message to reduce spam
            await context.message.delete()

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="level", aliases=["LEVEL", "lvl", "LVL"])
    async def level(self, context, *args):
        try:
            # using level on a target.
            if len(args) > 0:
                # use regex to extract only numbers to get their discord ID,
                # ex: <@348195501025394688> to 348195501025394688
                # create user instance with their target's discord ID, check database for their level field
                target_id = re.findall(r"\d+", args[0])[0]
                target = Users(target_id)
                if target.find_user() == 0:
                    await context.send("Target does not have account.")
                    return

                # fetch_user returns a User object that matches an id provided
                discord_member_target = await self.client.fetch_user(target_id)
                # embed the level retrieved from get_user_level(), set thumbnail to 64x64 version of target's id
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=discord_member_target.display_name, value=f"**Level** {target.get_user_level()}", inline=True,
                )
                thumb_url = (
                    f"https://cdn.discordapp.com/avatars/{discord_member_target.id}"
                    f"/{discord_member_target.avatar}.webp?size=64"
                )
                em.set_thumbnail(url=thumb_url)

                await context.send(context.author.mention, embed=em)

            # if they passed no parameter, get their own level
            else:
                # create user instance with their discord ID, check database for their level field
                user = Users(context.author.id)

                # embed the level retrieved from get_user_level(), set thumbnail to 64x64 version of user's id
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=context.author.display_name, value=f"**Level** {user.get_user_level()}", inline=True,
                )
                thumb_url = (
                    f"https://cdn.discordapp.com/avatars/{context.author.id}/{context.author.avatar}.webp?size=64"
                )
                em.set_thumbnail(url=thumb_url)

                await context.send(context.author.mention, embed=em)

        # Added this exception for debugging purposes.
        except Exception as e:
            msg = f"Not ok! {e.__class__} occurred"
            log.debug(msg)
            await context.send(f"{context.author.mention}```ml\nuse =level like so: **=level** or **=level @user**")
        finally:
            # delete original message to reduce spam
            await context.message.delete()

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="give", aliases=["DONATE", "GIVE", "pay", "donate", "PAY", "gift", "GIFT"])
    async def give(self, context, *args):
        # will automatically go to exception if all arguments weren't supplied correctly
        try:
            receiver_string = args[0]
            amnt = int(args[1])
            if amnt < 1:
                await context.send("Can’t GIFT DEBT!")
                return
            # create user instance with their discord ID, check database for their level field
            donator = Users(context.author.id)
            # use regex to extract only numbers from "receiver_string" to get their discord ID,
            # ex: <@348195501025394688> to 348195501025394688
            receiver = Users(re.findall(r"\d+", receiver_string)[0])

            # check if receiver has account
            if receiver.find_user() == 0:
                await context.send(
                    f"{context.author.mention} The target doesn't have an account." f"\nUse **=create** to make one."
                )
                return
            # check if donator has enough money for the donation
            # pass 0 to return integer version of money, see USERS.PY function
            if int(amnt) > donator.get_user_money(0):
                await context.send(
                    f"{context.author.mention} You don't have enough money for that donation..."
                    f" <a:pepehands:485869482602922021> "
                )
                return

            # pass the donation amount, pass the receiver user object, and pass the receiver's string name
            msg = context.author.mention + " " + donator.donate_money(int(amnt), receiver, receiver_string)
            # embed the donation message, put a heartwarming emoji size 64x64 as the thumbnail
            em = discord.Embed(title="", colour=0x607D4A)
            em.add_field(name="DONATION ALERT", value=msg, inline=True)
            em.set_thumbnail(url="https://cdn.discordapp.com/emojis/526815183553822721.webp?size=64")
            await context.send(embed=em)
            await context.message.delete()
        except Exception as e:
            msg = f"Not ok! {e.__class__} occurred"
            log.debug(msg)
            await context.send(
                f"{context.author.mention}```ml\nuse =give like so: **=give @user X**"
                f"    -- X being amnt of money to give```"
            )

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="stats", aliases=["battles", "BRECORDS", "STATS", "profile", "PROFILE", "gear", "GEAR"],
    )
    async def profile_stats(self, context, *args):
        try:
            # using stats on a target.
            if len(args) > 0:
                # use regex to extract only numbers to get their discord ID,
                # ex: <@348195501025394688> to 348195501025394688
                # create user instance with their target's discord ID, check database for their money field
                target_id = re.findall(r"\d+", args[0])[0]
                target = Users(target_id)
                if target.find_user() == 0:
                    await context.send("Target does not have account.")
                    return

                # fetch_user returns a User object that matches an id provided
                discord_member_target = await self.client.fetch_user(target_id)
                target_avatar_url = discord_member_target.avatar_url

                # embed the statistics retrieved from get_user_stats(), set thumbnail to target's id
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=discord_member_target.display_name, value=target.get_user_stats(), inline=True,
                )
                em.set_thumbnail(url=target_avatar_url)

                await context.send(context.author.mention, embed=em)

            # if they passed no parameter, or user was not found, get their own records
            else:
                # create user instance with their discord ID, check database for their level field
                user = Users(context.author.id)

                # embed the statistics retrieved from get_user_stats(), set thumbnail to user's id
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=context.author.display_name, value=user.get_user_stats(), inline=True,
                )
                em.set_thumbnail(url=context.author.avatar_url)

                await context.send(context.author.mention, embed=em)

        except Exception as e:
            msg = f"Not ok! {e.__class__} occurred"
            log.debug(msg)
            await context.send(
                f"{context.author.mention}```ml\nuse =profile like so: **=profile** or **=profile @user**"
            )

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="levelup", aliases=["lup", "LEVELUP"])
    async def levelup(self, context):
        # create instance of user who wants to level-up
        user = Users(context.author.id)
        # get the user's current level
        # calculate the cost of their next level-up
        user_level = user.get_user_level(0)  # get int version of level, SEE USERS.PY
        # level up cost algorithms, inspired by D&D algorithm

        if user_level == 1:
            level_up_cost = 399
        elif user_level in range(2, 8):
            level_up_cost = int(300 * ((user_level + 1) ** 1.8) - (300 * user_level))
        elif user_level in range(8, 15):
            level_up_cost = int(300 * ((user_level + 1) ** 1.9) - (300 * user_level))
        elif user_level in range(15, 25):
            level_up_cost = int(300 * ((user_level + 1) ** 2.2) - (300 * user_level))
        elif user_level in range(25, 34):
            level_up_cost = int(300 * ((user_level + 1) ** 2.4) - (300 * user_level))
        elif user_level in range(34, 50):
            level_up_cost = int(300 * ((user_level + 1) ** 2.6) - (300 * user_level))
        elif user_level == 50:
            await self.client.say("You are already level 50, the max level!")
            return

        # check if they have enough money for a level-up
        if user.get_user_money(0) < level_up_cost:
            error_msg = await context.send(
                f"{context.author.mention} Not enough money for level-up... <a:pepehands:485869482602922021>\n"
                f"** **\nAccount balance: {user.get_user_money()}\nLevel **{user_level + 1}"
                f"** requires: **${level_up_cost:,}**"
            )
            # wait 15 seconds then delete error message and original message to reduce spam
            await asyncio.sleep(15)
            await error_msg.delete()
            await context.message.delete()
            return

        # passed conditional, so they have enough money to level up
        # confirm if they really want to level-up
        msg = (
            f"\nAccount balance: {user.get_user_money()}\nLevel **{user_level + 1}"
            f"** requires: **${level_up_cost:,}**\n** **\n** **\nDo you want to level-up?"
            f" Type **confirm** to confirm."
        )

        # embed the confirmation prompt, set thumbnail to user's id of max size
        em = discord.Embed(description=msg, colour=0x607D4A)
        thumb_url = f"https://cdn.discordapp.com/avatars/{context.author.id}/{context.author.avatar}.webp?size=1024"
        em.set_thumbnail(url=thumb_url)

        await context.send(context.author.mention, embed=em)

        # wait for user's input
        # message is the event name we're waiting for.

        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        confirm = await self.client.wait_for("message", check=is_author, timeout=60)
        if confirm.clean_content.upper() == "CONFIRM":
            # check if they tried to exploit the code by spending all their money before confirming
            if user.get_user_money(0) < level_up_cost:
                await context.send(f"{context.author.mention} You spent money before confirming...")
                return
            # deduct the level-up cost from their account
            user.update_user_money(level_up_cost * -1)
            # embed the confirmation message, set thumbnail to user's id of size 64x64
            # increase level by 1 and print new level
            em = discord.Embed(title="", colour=0x607D4A)
            em.add_field(
                name=context.author.display_name, value=user.update_user_level(), inline=True,
            )
            thumb_url = f"https://cdn.discordapp.com/avatars/{context.author.id}/{context.author.avatar}.webp?size=64"
            em.set_thumbnail(url=thumb_url)
            await context.send(embed=em)
        else:
            await context.send(f"{context.author.mention} Cancelled level-up.")

    @has_account()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(name="daily", aliases=["DAILY", "dailygamble"])
    async def daily(self, context):
        # create instance of user who wants to get their daily money
        user = Users(context.author.id)
        # get the user's current level
        # calculate the cost of their next level-up
        user_level = user.get_user_level(0)  # get int version of level, SEE USERS.PY
        dailyreward = user_level * 60

        msg = (
            f"<a:worryswipe:525755450218643496> Daily **${dailyreward}"
            f"** received! <a:worryswipe:525755450218643496>\n{user.update_user_money(dailyreward)}"
        )

        # embed the confirmation message, set thumbnail to user's id
        em = discord.Embed(title="", colour=0x607D4A)
        em.add_field(name=context.author.display_name, value=msg, inline=True)
        em.set_thumbnail(url=context.author.avatar_url)
        await context.send(embed=em)

    @has_voted()
    @has_account()
    @commands.cooldown(1, 43200, commands.BucketType.user)
    @commands.command(name="daily2", aliases=["DAILY2", "bonus", "votebonus"])
    async def daily2(self, context):
        # create instance of user who earned their vote bonus
        user = Users(context.author.id)
        # get the user's current level
        user_level = user.get_user_level(0)  # get int version of level, SEE USERS.PY
        dailyreward = user_level * 50

        msg = (
            f"<a:worryswipe:525755450218643496> Daily **${dailyreward}"
            f"** received! <a:worryswipe:525755450218643496>\n{user.update_user_money(dailyreward)}"
        )

        # embed the confirmation message, set thumbnail to user's id
        em = discord.Embed(title="", colour=0x607D4A)
        em.add_field(
            name=f"Thanks for voting, {context.author.display_name}", value=msg, inline=True,
        )
        em.set_thumbnail(url=context.author.avatar_url)
        await context.send(embed=em)

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="toggle", aliases=["togglepeace", "TOGGLEPEACE", "peace", "PEACE"],
    )
    async def toggle_peace(self, context):
        # create instance of user who wants to get their daily money
        user = Users(context.author.id)
        user_peace_status = user.get_user_peace_status()
        user_peace_cooldown = user.get_user_peace_cooldown()
        if user_peace_status == 0 and user_peace_cooldown == 0:
            msg = (
                ":dove: Would you like to enable peace status? :dove:\n\nType **confirm** to enter peace mode\n"
                "Type **cancel** to cancel\n\n"
                "_Note: \u200B \u200B \u200B This makes you exempt from users who use =rob @user "
                "\nNote2: \u200B In exchange, you will not be able to =rob @user"
                "\nNote3: You can still use =rob or be robbed randomly from =rob"
                "\nNote4: If enabled, cannot exit peace mode until Monday at 7am_"
            )
            # embed the confirmation message, set thumbnail to user's id
            em = discord.Embed(title="", colour=0x607D4A)
            em.add_field(name=context.author.display_name, value=msg, inline=True)
            em.set_thumbnail(url=context.author.avatar_url)
            await context.send(embed=em)

            # wait for a "confirm" response from the user to process the peace toggle
            # if it is not "confirm", cancel toggle

            # helper to check if it's the author that it's responding.
            def is_author(m):
                return m.author == context.author and m.channel == context.channel

            response = await self.client.wait_for("message", check=is_author, timeout=20)
            if response.clean_content.upper() == "CONFIRM":
                user.toggle_user_peace_status()
                user.update_user_peace_cooldown()
                confirmation = (
                    ":dove: You are now **in peace** status :dove:"
                    "\n\nYou are **unable** to turn it off until Monday at 7 AM PST!"
                )

                # embed the confirmation string, add the user's avatar to it, and send it
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=context.author.display_name, value=confirmation, inline=True,
                )
                em.set_thumbnail(url=context.author.avatar_url)
                await context.send(embed=em)
                return
            else:
                await context.send(f"{context.author.mention} Cancelled peace toggle-on!")
                return

        elif user_peace_status == 1 and user_peace_cooldown == 0:
            msg = (
                ":dove: You are currently **in peace** status and **able** to turn it off :dove:"
                "\n\nType **confirm** to turn off peace mode\nType **cancel** to cancel\n\n"
                "_Note: This will enable users to use =rob @user on you_"
            )
            # embed the confirmation message, set thumbnail to user's id
            em = discord.Embed(description=msg, colour=0x607D4A)
            em.set_thumbnail(url=context.author.avatar_url)
            await context.send(embed=em)

            # wait for a "confirm" response from the user to process the peace toggle
            # if it is not "confirm", cancel toggle

            # helper to check if it's the author that it's responding.
            def is_author(m):
                return m.author == context.author and m.channel == context.channel

            response = await self.client.wait_for("message", check=is_author, timeout=20)
            if response.clean_content.upper() == "CONFIRM":
                user.toggle_user_peace_status()
                confirmation = (
                    ":dove: You are now **out of peace** status :dove:\n\n_Note: =rob @user is now available_"
                )

                # embed the confirmation string, add the user's avatar to it, and send it
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(
                    name=context.author.display_name, value=confirmation, inline=True,
                )
                em.set_thumbnail(url=context.author.avatar_url)
                await context.send(embed=em)
                return
            else:
                await context.send(f"{context.author.mention} Cancelled peace toggle-off!")
                return

        elif user_peace_cooldown == 1:
            msg = (
                ":dove: You are currently **in peace** status :dove:"
                "\nYou are **unable** to turn it off until Monday at 7 AM PST!"
            )
            # embed the confirmation message, set thumbnail to user's id
            em = discord.Embed(description=msg, colour=0x607D4A)
            em.set_thumbnail(url="https://cdn.discordapp.com/emojis/440598341877891083.png?size=40")
            await context.send(embed=em)
            return

    @has_account()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="rankings", aliases=["ranks", "leaderboards", "lb"])
    async def ranks(self, context):
        # create instance of user who wants to view rankings
        user = Users(context.author.id)
        # retrieve top 15 ranked players
        rankings = user.get_user_ranks()
        # declare variables we will use as columns for the leaderboards
        name_field_column = ""
        win_loss_column = ""
        # set counter to properly display rank numbers
        counter = 1

        # iterate through the top 15 ranked players and retrieve their specific stats
        for rank in rankings:
            # initiate each ranked player
            user = Users(str(rank[0]))

            # store their stats in temporary variables
            (
                weapon_level,
                helmet_level,
                chest_level,
                boots_level,
                battles_lost,
                battles_won,
                total_winnings,
            ) = user.get_user_stats(0)
            # format money for commas
            total_winnings = f"{total_winnings:,}"
            # try to retrieve user's level, if failed, skip to next iteration
            try:
                user_level = user.get_user_level(0)
            except:
                continue

            # get the "member" discord object in order to retrieve the user's current discord name
            discordmember = await self.client.fetch_user(rank[0])
            ranker_name = str(discordmember.name)
            # remove everything except alphanumerics from the user's current discord name
            ranker_name = re.sub(r"\W+", "", ranker_name)

            # format the 2 columns for the leaderboards
            name_field_column += f"{counter}. {ranker_name[:15]} \u200B \u200B (_lvl: {user_level}_ ) \u200B \u200B \n"
            win_loss_column += f"${total_winnings}/{battles_won}/{battles_lost}\n"
            counter += 1

        # embed the ranking columns
        em = discord.Embed(title="", colour=0x607D4A)
        em.add_field(name="Top 15 Fighters", value=name_field_column, inline=True)
        em.add_field(name="Winnings/W/L", value=win_loss_column, inline=True)
        # set embedded thumbnail to an upwards trend chart
        em.set_thumbnail(url="https://cdn.shopify.com/s/files/1/0185/5092/products/objects-0104_800x.png?v=1369543363")
        await context.send(embed=em)


def setup(client):
    client.add_cog(Account(client))
