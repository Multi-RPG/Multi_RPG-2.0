#!/usr/bin/env python3
import re
import discord
import asyncio
import logging

from discord.ext import commands
from discord import option
from typing import Union

# from DiscordBotsOrgApi import DiscordBotsOrgAPI
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

    @commands.slash_command(
        name="create",
        description="Create an account.",
        aliases=["register"],
    )
    async def register(self, context):
        # create new user instance with their discord ID to store in database
        new_user = Users(context.author.id)
        if new_user.find_user() == 1:
            await context.respond("<:worrymag1:531214786646507540> You **already** have an account registered!")
            return

        await context.respond(
            embed=self._basic_message_embed(
                name=context.author.display_name, value=new_user.add_user(), url=context.author.display_avatar
            )
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="money",
        description="Display money balance.",
        aliases=["m", "MONEY"],
    )
    @option(name="user", type=discord.User, required=False)
    async def money(self, context, user):
        if user is None:
            discord_user = context.author
            user = Users(discord_user.id)
            if user.find_user() == 0:
                await context.respond("You do not have an account.")
                return

            await context.respond(
                embed=self._basic_message_embed(
                    name=discord_user.display_name,
                    value=f"**:moneybag: ** {user.get_user_money()}",
                    url=discord_user.display_avatar,
                )
            )
        else:
            target = Users(user.id)
            if target.find_user() == 0:
                await context.respond("Target does not have an account.")
                return

            await context.respond(
                embed=self._basic_message_embed(
                    name=user.display_name, value=f"**:moneybag: ** {target.get_user_money()}", url=user.display_avatar
                )
            )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="level",
        description="Display level.",
        aliases=["LEVEL", "lvl", "LVL"],
    )
    @option(name="user", type=discord.User, required=False)
    async def level(self, context, user):
        if user is None:
            discord_user = context.author
            user = Users(discord_user.id)
            if user.find_user() == 0:
                await context.respond("you do not have an account.")
                return

            await context.respond(
                embed=self._basic_message_embed(
                    name=discord_user.display_name,
                    value=f"**Level** {user.get_user_level()}",
                    url=discord_user.display_avatar,
                )
            )
        else:
            target = Users(user.id)
            if target.find_user() == 0:
                await context.respond("Target does not have an account.")
                return

            await context.respond(
                embed=self._basic_message_embed(
                    name=user.display_name,
                    value=f"**Level** {target.get_user_level()}",
                    url=user.display_avatar,
                )
            )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="give",
        description="Give own money to other user.",
        aliases=["DONATE", "GIVE", "pay", "donate", "PAY", "gift", "GIFT"],
    )
    @option(name="user", type=discord.User, required=True)
    @option(name="amount", type=int, required=True)
    async def give(self, context, user, amount):
        receiver = Users(user.id)
        # check if receiver has account
        if receiver.find_user() == 0:
            await context.respond(f"The target doesn't have an account." f"\nUse **/create** to make one.")
            return

        # check if donator has account
        donator = Users(context.author.id)
        if donator.find_user() == 0:
            await context.respond(f"You don't have an account." f"\nUse **/create** to make one.")
            return

        if amount < 1:
            await context.respond("Can’t GIFT DEBT!")
            return

        if amount > donator.get_user_money(0):
            await context.respond(f"You don't have enough money for that donation... <a:pepehands:485869482602922021>")
            return

        msg = f"{donator.donate_money(amount, receiver, user.display_name)}"
        await context.respond(
            embed=self._basic_message_embed(
                name="DONATION ALERT",
                value=msg,
                url="https://cdn.discordapp.com/emojis/526815183553822721.webp?size=64",
            )
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="stats",
        description="Display profile stats.",
        aliases=["battles", "BRECORDS", "STATS", "profile", "PROFILE", "gear", "GEAR"],
    )
    @option(name="user", type=discord.User, required=False)
    async def profile_stats(self, context, user):
        if user is None:
            discord_user = context.author
            user = Users(discord_user.id)
            if user.find_user() == 0:
                await context.respond("You do not have an account.")
                return

            await context.respond(
                embed=self._basic_message_embed(
                    name=discord_user.display_name,
                    value=user.get_user_stats(),
                    url=discord_user.display_avatar,
                )
            )

        else:
            target = Users(user.id)
            if target.find_user() == 0:
                await context.respond("Target does not have an account.")
                return

            await context.respond(
                embed=self._basic_message_embed(
                    name=user.display_name,
                    value=target.get_user_stats(),
                    url=user.display_avatar,
                )
            )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="levelup",
        description="Level the account up.",
        aliases=["lup", "LEVELUP"],
    )
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
            await self.respond("You are already level 50, the max level!")
            return

        # check if they have enough money for a level-up
        if user.get_user_money(0) < level_up_cost:
            error_msg = await context.respond(
                f"{context.author.mention} Not enough money for level-up... <a:pepehands:485869482602922021>\n"
                f"** **\nAccount balance: {user.get_user_money()}\nLevel **{user_level + 1}"
                f"** requires: **${level_up_cost:,}**"
            )
            # wait 15 seconds then delete error message and original message to reduce spam
            await asyncio.sleep(15)
            await context.delete()
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
        await context.respond(context.author.mention, embed=em)

        # wait for user's input
        # message is the event name we're waiting for.

        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        try:
            confirm = await self.client.wait_for("message", check=is_author, timeout=30)
            if confirm.clean_content.upper() == "CONFIRM":
                # check if they tried to exploit the code by spending all their money before confirming
                if user.get_user_money(0) < level_up_cost:
                    await context.respond("You spent money before confirming...")
                    return
                # deduct the level-up cost from their account
                user.update_user_money(level_up_cost * -1)
                # embed the confirmation message, set thumbnail to user's id of size 64x64
                # increase level by 1 and print new level
                await context.send(
                    embed=self._basic_message_embed(
                        name=context.author.display_name,
                        value=user.update_user_level(),
                        url=context.author.display_avatar,
                    )
                )
            else:
                await context.respond("I didn't get your answer. Please try again.")
        except asyncio.TimeoutError:
            await context.respond("Cancelled level-up.")

    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.slash_command(name="daily", description="Get daily money.", aliases=["DAILY", "dailygamble"])
    async def daily(self, context):
        # create instance of user who wants to get their daily money
        user = Users(context.author.id)
        if user.find_user() == 0:
            await context.respond("You do not have an account.")
            return

        # get the user's current level
        # calculate the cost of their next level-up
        user_level = user.get_user_level(0)  # get int version of level, SEE USERS.PY
        dailyreward = user_level * 60

        msg = (
            f"<a:worryswipe:525755450218643496> Daily **${dailyreward}"
            f"** received! <a:worryswipe:525755450218643496>\n{user.update_user_money(dailyreward)}"
        )
        await context.respond(
            embed=self._basic_message_embed(
                name=context.author.display_name, value=msg, url=context.author.display_avatar
            )
        )

    @has_voted()
    @commands.cooldown(1, 43200, commands.BucketType.user)
    @commands.slash_command(name="daily2", description="Get daily money.", aliases=["DAILY2", "bonus", "votebonus"])
    async def daily2(self, context):
        # create instance of user who earned their vote bonus
        user = Users(context.author.id)
        if user.find_user() == 0:
            await context.respond("You do not have an account.")
            return

        # get the user's current level
        user_level = user.get_user_level(0)  # get int version of level, SEE USERS.PY
        dailyreward = user_level * 50

        msg = (
            f"<a:worryswipe:525755450218643496> Daily **${dailyreward}"
            f"** received! <a:worryswipe:525755450218643496>\n{user.update_user_money(dailyreward)}"
        )
        await context.respond(
            embed=self._basic_message_embed(
                name=f"Thanks for voting, {context.author.display_name}", value=msg, url=context.author.display_avatar
            )
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(
        name="toggle",
        description="Toggle peace on and off.",
        aliases=["togglepeace", "TOGGLEPEACE", "peace", "PEACE"],
    )
    async def toggle_peace(self, context):
        # create instance of user who wants to get their daily money
        user = Users(context.author.id)
        if user.find_user() == 0:
            await context.respond("You do not have an account.")
            return

        user_peace_status = user.get_user_peace_status()
        user_peace_cooldown = user.get_user_peace_cooldown()
        if user_peace_status == 0 and user_peace_cooldown == 0:
            msg = (
                ":dove: Would you like to enable peace status? :dove:\n\nType **confirm** to enter peace mode\n"
                "Type anything else to cancel\n\n"
                "_Note: \u200B \u200B \u200B This makes you exempt from users who use =rob @user "
                "\nNote2: \u200B In exchange, you will not be able to =rob @user"
                "\nNote3: You can still use =rob or be robbed randomly from =rob"
                "\nNote4: If enabled, cannot exit peace mode until Monday at 7am_"
            )
            await context.respond(
                embed=self._basic_message_embed(
                    name=context.author.display_name, value=msg, url=context.author.display_avatar
                )
            )

            # helper to check if it's the author that it's responding.
            def is_author(m):
                return m.author == context.author and m.channel == context.channel

            try:
                # wait for a "confirm" response from the user to process the peace toggle
                # if it is not "confirm", cancel toggle
                response = await self.client.wait_for("message", check=is_author, timeout=20)
                if response.clean_content.upper() == "CONFIRM":
                    user.toggle_user_peace_status()
                    user.update_user_peace_cooldown()
                    confirmation = (
                        ":dove: You are now **in peace** status :dove:"
                        "\n\nYou are **unable** to turn it off until Monday at 7 AM PST!"
                    )
                    await context.send(
                        embed=self._basic_message_embed(
                            name=context.author.display_name, value=confirmation, url=context.author.display_avatar
                        )
                    )
                else:
                    await context.respond("Cancelled peace toggle-on.")
            except asyncio.TimeoutError:
                await context.respond("Cancelled peace toggle-on!")

        elif user_peace_status == 1 and user_peace_cooldown == 0:
            msg = (
                ":dove: You are currently **in peace** status and **able** to turn it off :dove:"
                "\n\nType **confirm** to turn off peace mode\nType **cancel** to cancel\n\n"
                "_Note: This will enable users to use =rob @user on you_"
            )
            # embed the confirmation message, set thumbnail to user's id
            em = discord.Embed(description=msg, colour=0x607D4A)
            em.set_thumbnail(url=context.author.avatar_url)
            await context.response(embed=em)

            # helper to check if it's the author that it's responding.
            def is_author(m):
                return m.author == context.author and m.channel == context.channel

            try:
                # wait for a "confirm" response from the user to process the peace toggle
                # if it is not "confirm", cancel toggle
                response = await self.client.wait_for("message", check=is_author, timeout=20)
                if response.clean_content.upper() == "CONFIRM":
                    user.toggle_user_peace_status()
                    confirmation = (
                        ":dove: You are now **out of peace** status :dove:\n\n_Note: =rob @user is now available_"
                    )
                    await context.send(
                        embed=self._basic_message_embed(
                            name=context.author.display_name, value=confirmation, url=context.author.display_avatar
                        )
                    )
                else:
                    await context.respond("Cancelled peace toogle-on.")

            except asyncio.TimeoutError:
                await context.respond("Cancelled peace toggle-on!")

        elif user_peace_cooldown == 1:
            msg = (
                ":dove: You are currently **in peace** status :dove:"
                "\nYou are **unable** to turn it off until Monday at 7 AM PST!"
            )
            # embed the confirmation message, set thumbnail to user's id
            em = discord.Embed(description=msg, colour=0x607D4A)
            em.set_thumbnail(url="https://cdn.discordapp.com/emojis/440598341877891083.png?size=40")
            await context.response(embed=em)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.slash_command(name="rankings", description="Display ranking.", aliases=["ranks", "leaderboards", "lb"])
    async def ranks(self, context):
        # create instance of user who wants to view rankings
        user = Users(context.author.id)
        if user.find_user() == 0:
            await context.respond("You do not have an account.")
            return

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
            # FIXME: refactor this.
            try:
                user_level = user.get_user_level(0)
            except Exception as e:
                log.debug(f"[{type(e).__name__} {e}] - User not found.")
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
        await context.respond(embed=em)

    def _basic_message_embed(
        self,
        name: str,
        value: str,
        url: str,
        title: str = "",
        colour: Union[discord.Colour, int] = 0x607D4A,
        inline: bool = True,
    ):
        em = discord.Embed(title=title, colour=colour)
        em.add_field(
            name=name,
            value=value,
            inline=inline,
        )
        em.set_thumbnail(url=url)
        return em


def setup(client):
    client.add_cog(Account(client))
