#!/usr/bin/env python3
import asyncio
import discord
import math
import collections
import logging

from discord.ext import commands
from Users import Users
from Database import Database

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


help_msg = (
    "<a:worryswipe:525755450218643496>"
    " Pick an item number from **=shop** then use **=buy X**"
    " <a:worryswipe:525755450218643496>"
)


class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client

    @has_account()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(
        name="shop", description="view daily shop", brief="view the daily shop", aliases=["SHOP"],
    )
    async def shop(self, context):
        # connect to database file
        db = Database(0)
        db.connect()
        # get list of current shop items from database
        daily_items = db.get_shop_list()
        formatted_items = []

        # Emojis used for reaction
        Emoji_Reaction = collections.namedtuple("Emoji_Reaction", ["Left", "Right"])
        emoji = Emoji_Reaction("⬅️", "➡️")

        # for each item retreived from database, get the details of each one from the returned tuple
        for item in daily_items:

            item_id = item[0]
            item_name = item[1]
            item_type = item[2]
            item_lvl = item[3]
            item_price = item[4]

            if item_type == "weapon":
                item_emoji = "<:weapon1:532252764097740861>"
            elif item_type == "helmet":
                item_emoji = "<:helmet2:532252796255469588>"
            elif item_type == "chest":
                item_emoji = "<:chest5:532255708679503873>"
            else:
                item_emoji = "<:boots1:532252814953676807>"

            # have to insert encode \u200B for spaces when using discord encoding
            formatted_items.append(
                f"**Item {item_id}**: {item_name} (**Lvl {item_lvl}"
                f"**)\n\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B"
                f" \u200B \u200B \u200B __Type__: {item_emoji}\n\u200B \u200B \u200B \u200B"
                f" \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B"
                f" __Price__: **${item_price:,}**\n"
            )

        # place the first page of items into a string
        page1_str = ""
        for item in formatted_items[0:5]:
            page1_str += item

        # each page has max of 5 items, so get the total amount of pages our shop message will have
        total_pages = int(math.ceil(len(formatted_items) / 5.0))

        # embed first set of 5 items, send the message
        em = discord.Embed(title="", colour=0x607D4A)
        # get the current page/total_page and add it to the embedded page's title
        field_name = f"Shop (Page {1}/{total_pages})"
        em.add_field(name=field_name, value=page1_str, inline=True)
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/525164940231704577.gif?size=64")
        # send the first page of items in a message
        intro_msg = await context.send(f"{context.author.mention} {help_msg}")
        msg = await context.send(embed=em)

        # if there is more than 5 items, we need more than 1 page.
        if len(formatted_items) > 5:
            # add a right arrow emoji to the first page's message, and wait for the author to click it
            await msg.add_reaction(emoji=emoji.Right)

            # Checks if the user adding the reaction is the message author.
            def is_author(reaction, user):
                return user == context.author and str(reaction.emoji) in emoji

            try:
                # In the new API, waif_for returns a tuple. The first element is the emoji (reaction).
                reaction, user = await self.client.wait_for("reaction_add", check=is_author, timeout=30)

                # counter will represent the last item number on current page
                # it will be used as indexes of formatted_items[] for changing pages
                counter = 5
                current_page_number = 1
                # while a reaction is provided and not timed out
                while reaction:
                    # delete the previous page message
                    await msg.delete()
                    # reset the items string
                    page_str = ""

                    # if user reacted to go to next page
                    if str(reaction) == emoji.Right:
                        current_page_number += 1
                        # set the new indexes to next 5 items indexes, store the new range into a string
                        for item in formatted_items[counter : counter + 5]:
                            page_str += item
                        # clear the embed fields for the new page of items, add the new one, and send it
                        em.clear_fields()
                        # get the current page/total_page and add it to the embedded page's title
                        field_name = f"Shop (Page {current_page_number}/{total_pages})"
                        em.add_field(name=field_name, value=page_str, inline=True)
                        msg = await context.send(embed=em)

                        # add 5 to the counter to indicate new index
                        counter += 5
                        # add emoji to go to previous page if desired
                        await msg.add_reaction(emoji=emoji.Left)
                        # if the current page number isn't the page count, there is a next page
                        if not current_page_number == total_pages:
                            await msg.add_reaction(emoji=emoji.Right)

                    # if user reacted to go to previous page
                    elif str(reaction) == emoji.Left:
                        current_page_number -= 1
                        # set the new indexes to previous 5 items indexes, store the new range into a string
                        for item in formatted_items[counter - 10 : counter - 5]:
                            page_str += item
                        # clear the embed fields for the new page of items, add the new one, and send it
                        em.clear_fields()
                        # get the current page/total_page and add it to the embedded page's title
                        field_name = f"Shop (Page {current_page_number}/{total_pages})"
                        em.add_field(name=field_name, value=page_str, inline=True)
                        msg = await context.send(embed=em)

                        # subtract 5 from the counter to indicate new index
                        counter -= 5
                        # if current page number is not page 1, there is a previous page
                        if not current_page_number == 1:
                            await msg.add_reaction(emoji=emoji.Left)
                        # add emoji to go to next page if desired
                        await msg.add_reaction(emoji=emoji.Right)

                    # wait for next reaction then restart loop if no timeout
                    # Checks if the user adding the reaction is the message author.
                    def is_author(reaction, user):
                        return user == context.author and str(reaction.emoji) in emoji

                    reaction, user = await self.client.wait_for("reaction_add", check=is_author, timeout=30)

            except asyncio.TimeoutError:
                log.debug("Timeout")

            # This is called regardless.
            finally:
                await asyncio.sleep(30)
                await intro_msg.delete()
                await msg.delete()

    @has_account()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(
        name="buy", description="buy an item from the daily shop", brief="buy an item from the shop", aliases=["BUY"],
    )
    async def buy(self, context, *args):
        # connect to database file
        db = Database(0)
        db.connect()

        # try to retrieve the item number the user should have provided as a parameter
        try:
            item_id = int(args[0])
        except:
            error_msg = await context.send(f"{context.author.mention} {help_msg}")
            await asyncio.sleep(7)
            await error_msg.delete()
            await context.message.delete()
            return

        # get the specified item's stats from the database
        item = db.get_shop_item(item_id)
        # if the specified item number isn't in the Shop table in the database,
        # inform user to check the daily shop again because item doesn't exist and return
        if not item:
            error_msg = await context.send(
                "<:worrymag1:531214786646507540> Couldn't find that item "
                "<:worrymag2:531214802266095618>\nCheck **=shop** again..."
            )
            await asyncio.sleep(7)
            await error_msg.delete()
            await context.message.delete()
            return

        # make variables for all the details on the specified item
        item_name = item[1]
        item_type = item[2]
        item_lvl = item[3]
        item_price = item[4]
        # create instance of user
        user = Users(context.author.id)

        # if user doesn't have enough money for the specified item, inform user how much more money they need + return
        if user.get_user_money(0) < item_price:
            difference = str(item_price - user.get_user_money(0))
            error_msg = (
                f" <:worrymag1:531214786646507540> Not enough money!"
                f" You need **${difference}** more for that item! <:worrymag2:531214802266095618>"
            )
            em = discord.Embed(description=error_msg, colour=0x607D4A)
            await context.send(context.author.mention, embed=em)
            return

        # if user's item level is already greater than or equal to the item the user is trying to buy,
        # inform user + return because the user should not be able to downgrade
        error_msg = (
            "<:worrymag1:531214786646507540> Your current equipped item is already **better or equal** to that! "
            "<:worrymag1:531214786646507540>"
        )
        # retrieve the first four values [0-3] returned from get_user_stats and store them into variables
        user_weapon_lvl, user_helmet_lvl, user_chest_lvl, user_boots_lvl = user.get_user_stats(0)[0:4]
        # compare user's item level against specified item's level, based off item type the user is trying to purchase
        if item_type == "weapon":
            if user_weapon_lvl >= item_lvl:
                em = discord.Embed(description=error_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return
            item_emoji = "<:weapon1:532252764097740861>"
        elif item_type == "helmet":
            if user_helmet_lvl >= item_lvl:
                em = discord.Embed(description=error_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return
            item_emoji = "<:helmet2:532252796255469588>"
        elif item_type == "chest":
            if user_chest_lvl >= item_lvl:
                em = discord.Embed(description=error_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return
            item_emoji = "<:chest5:532255708679503873>"
        else:
            if user_boots_lvl >= item_lvl:
                em = discord.Embed(description=error_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return
            item_emoji = "<:boots1:532252814953676807>"

        # draft the confirmation prompt string
        # have to insert encode \u200B for spaces when using discord encoding
        confirmation_prompt = (
            f"Type **confirm** to buy:\n\n__{item_name}__ (**Lvl {item_lvl}"
            f"**)\n \u200B \u200B \u200B \u200B \u200B \u200B \u200B"
            f" \u200B \u200B \u200B \u200B \u200B \u200B \u200B __Type__: {item_emoji}"
            f"\n \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B\u200B"
            f" \u200B \u200B \u200B \u200B \u200B __Price__: **${item_price}**\n"
        )

        # embed the confirmation prompt and send it
        em = discord.Embed(description=confirmation_prompt, colour=0x607D4A)
        prompt_msg = await context.send(context.author.mention, embed=em)

        # wait for a "confirm" response from the user to process the purchase
        # if it is not "confirm", cancel transaction
        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        response = await self.client.wait_for("message", check=is_author, timeout=20)
        if response.clean_content.upper() == "CONFIRM":
            # check if they tried to exploit the code by spending all their money before confirming
            if user.get_user_money(0) < item_price:
                await context.send(f"{context.author.mention} You spent money before confirming...")
                return
            # subtract the item's price from user's bank account
            confirmation = (
                f"<:worrysign10:531221748964786188> Bought **{item_name}**! <:worrysign10:531221748964786188>\n"
            )
            # update user's item level for that item type bought
            confirmation += (
                f"{user.update_user_battle_gear(item_type, item_lvl)}\n{user.update_user_money(item_price * -1)}"
            )

            # embed the confirmation string, add the user's avatar to it, and send it
            em = discord.Embed(title="", colour=0x607D4A)
            em.add_field(
                name=context.author.display_name, value=confirmation, inline=True,
            )
            em.set_thumbnail(url=context.author.avatar_url)
            await context.send(embed=em)
        else:
            await context.send(f"{context.author.mention} Cancelled purchase!")

        # clean up messages to reduce spam in channel
        await response.delete()
        await prompt_msg.delete()


def setup(client):
    client.add_cog(Shop(client))
