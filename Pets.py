#!/usr/bin/env python3
import asyncio
import re
import discord
from discord.ext import commands
from Users import Users
from profanityfilter import ProfanityFilter
from random import choices


# short decorator function declaration, confirm that command user has an account in database
def has_account():
    def predicate(ctx):
        user = Users(ctx.message.author.id)
        if user.find_user() == 0:
            return False
        else:
            return True

    return commands.check(predicate)


# short decorator function declaration, confirm that command user has a pet in database
def has_pet():
    def predicate(ctx):
        user = Users(ctx.message.author.id)
        if user.find_pet() == 0:
            return False
        else:
            return True

    return commands.check(predicate)


class Pets(commands.Cog):
    def __init__(self, client):
        self.client = client

    """ADOPT A PET FUNCTION"""

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="adopt", description="adopt a pet and raise it for rewards", brief="can use =adopt", aliases=["ADOPT"],
    )
    async def adopt_pet(self, context):
        # create instance of the user who wishes to feed their pet
        pet_owner = Users(context.author.id)

        if pet_owner.find_pet() == 1:
            msg = await context.send("Failed! You already have a pet!")
            await asyncio.sleep(5)
            await msg.delete()
            return

        intro_msg = "Welcome to the **Pet Shelter**!\n\nPlease enter your desired pet name now:"
        # embed intro message, then overwrite the variable with the actual message object
        em = discord.Embed(description=intro_msg, colour=0x607D4A)
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/746904102650249296.gif?size=128")
        await context.send(embed=em)

        # wait for user's pet name entry
        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        pet_name = await self.client.wait_for("message", check=is_author, timeout=60)
        # remove everything except alphanumerics from the user's pet name entry
        pet_name = re.sub(r"\W+", "", pet_name.clean_content)

        # create an object to scan profanity
        pf = ProfanityFilter()
        # while the pet name entry has profanity, prompt user to re-enter a name
        while not pf.is_clean(pet_name):
            await context.send("Pet name has profanity! Please enter a new one now:")
            # wait for user's new pet name entry
            pet_name = await self.client.wait_for("message", check=is_author, timeout=60)
            # remove everything except alphanumerics from the user's pet name entry
            pet_name = re.sub(r"\W+", "", pet_name.clean_content)

        adoption_msg = pet_owner.add_pet(pet_name[:15])
        # embed confirmation message
        em = discord.Embed(description=adoption_msg, colour=0x607D4A)
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/563872560308289536.png?v=1")
        await context.send(embed=em)

    """FEED PET FUNCTION"""

    @has_account()
    @has_pet()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(
        name="feed", description="feed your pet for XP", brief="can use =feed", aliases=["FEED"],
    )
    async def feed(self, context):
        # create instance of the user who wishes to feed their pet
        pet_owner = Users(context.author.id)
        # retrieve pet name
        pet_name = pet_owner.get_user_pet_name()
        # "feed" the pet by updating the pet's xp, then place updated xp in a variable
        new_pet_xp = pet_owner.update_user_pet_xp()
        # retrieve integer of pet's current level
        pet_level = pet_owner.get_user_pet_level(0)

        # calculate the current XP level up requirement for the user's pet
        level_up_cost = int(300 * ((pet_level + 1) ** 1.25) - (300 * pet_level))
        if new_pet_xp >= level_up_cost:
            new_pet_level = pet_owner.update_user_pet_level()
            confirmation_msg = (
                f"Fed **{pet_name}**. They leveled up and transformed!\n"
                f" They now have a higher chance to hunt for gear upgrades!"
                f"\n\n\nNew level: **{new_pet_level}**"
            )

            if new_pet_level == 2:
                pet_avatar = "https://cdn.discordapp.com/emojis/491930617823494147.png?v=1"
            elif new_pet_level == 3:
                pet_avatar = "https://cdn.discordapp.com/emojis/435032643772350464.png?v=1"
            elif new_pet_level == 4:
                pet_avatar = "https://cdn.discordapp.com/emojis/400690504104148992.png?v=1"
            else:
                pet_avatar = "https://cdn.discordapp.com/emojis/422845006232027147.png?v=1"

        else:
            if pet_level == 1:
                pet_avatar = "https://cdn.discordapp.com/emojis/563872560308289536.png?v=1"
            elif pet_level == 2:
                pet_avatar = "https://cdn.discordapp.com/emojis/491930617823494147.png?v=1"
            elif pet_level == 3:
                pet_avatar = "https://cdn.discordapp.com/emojis/435032643772350464.png?v=1"
            elif pet_level == 4:
                pet_avatar = "https://cdn.discordapp.com/emojis/400690504104148992.png?v=1"
            else:
                pet_avatar = "https://cdn.discordapp.com/emojis/422845006232027147.png?v=1"

            confirmation_msg = (
                f"Fed **{pet_name}**! They feel stuffed for today.\n\n\n**XP:** {new_pet_xp}" f"/{level_up_cost}"
            )

        # embed confirmation message
        em = discord.Embed(description=confirmation_msg, colour=0x607D4A)
        em.set_thumbnail(url=pet_avatar)
        await context.send(embed=em)

    """PET HUNT LOOT FUNCTION"""

    @has_account()
    @has_pet()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    @commands.command(
        name="hunt", description="command your pet to hunt for loot", brief="can use =hunt", aliases=["HUNT", "Hunt"],
    )
    async def hunt(self, context):
        # create instance of the user who wishes for their pet to hunt rewards
        pet_owner = Users(context.author.id)
        # retrieve pet name
        pet_name = pet_owner.get_user_pet_name()
        # retrieve integer of pet's current level
        pet_level = pet_owner.get_user_pet_level(0)

        # 1. set the pet's avatar based on the pet's level
        # 2. randomly choose if the pet's hunt will find money or gear
        # note: a higher level pet will have a higher chance of finding gear
        if pet_level == 1:
            pet_avatar = "https://i.imgur.com/BknfCkz.gif"
            loot = choices([1, 2], [0.90, 0.10])
        elif pet_level == 2:
            pet_avatar = "https://i.imgur.com/vm7GjwZ.gif"
            loot = choices([1, 2], [0.87, 0.13])
        elif pet_level == 3:
            pet_avatar = "https://i.imgur.com/uhgLfqE.gif"
            loot = choices([1, 2], [0.85, 0.15])
        elif pet_level == 4:
            pet_avatar = "https://i.imgur.com/00ZQwGP.gif"
            loot = choices([1, 2], [0.83, 0.17])
        else:
            pet_avatar = "https://i.imgur.com/iELOcfw.gif"
            loot = choices([1, 2], [0.80, 0.20])

        # remove brackets from returned value of choices() function
        loot = int(re.findall(r"\d+", str(loot))[0])

        # if it was decided that the loot would be a money reward, reward the pet owner with money
        if loot == 1:
            reward_msg = (
                f"**{pet_name}** was unable to hunt any gear upgrades in the woods..."
                f"\nBut, they located a :moneybag: on their journey!"
            )
            # get int version of level and multiply it by 35 for the money reward
            reward = pet_owner.get_user_level(0) * 35
            pet_owner.update_user_money(reward)

            reward_msg += (
                f"\n\n<a:worryswipe:525755450218643496> "
                f"You received **${reward}** from your pet's efforts."
                f" <a:worryswipe:525755450218643496>"
            )
        # if it was decided that the loot would be a gear upgrade reward, upgrade the pet owner's lowest gear item
        else:
            reward_msg = (
                f"**{pet_name}** located a gear upgrade in the woods for you!"
                f"\n\n\n<a:worryHype:487059927731273739> "
            )

            # if they are awarded a gear upgrade (which happens in this conditional), we need to do a few things:
            # 1. retrieve the pet owner's lowest level gear item
            # 2. then offer the pet owner a corresponding item 1 gear point above the item

            # assign each variable from the sql query to retrieve the pet owner's gear levels
            (
                weapon_level,
                helmet_level,
                chest_level,
                boots_level,
                battles_lost,
                battles_won,
                total_winnings,
            ) = pet_owner.get_user_stats(0)

            # put the point levels of each gear piece they possess in a list
            list = (weapon_level, helmet_level, chest_level, boots_level)
            # retrieve the index of the lowest point item they possess
            index_smallest = list.index(min(list))

            # if the user has at least level 10 gear pieces of all types, give them money reward and return
            if list[index_smallest] == 10:
                reward_msg = (
                    f"**{pet_name}** failed to hunt gear. Level 10 gear is the limit for hunt upgrades."
                    f"\nCheck =shop for level 11 and level 12 items."
                    f"\nBut, they located a :moneybag: on their journey!"
                )
                # get int version of level and multiply it by 35 for the money reward
                reward = pet_owner.get_user_level(0) * 35
                pet_owner.update_user_money(reward)

                reward_msg += (
                    f"\n\n<a:worryswipe:525755450218643496> "
                    f"You received **${reward}** from your pet's efforts."
                    f" <a:worryswipe:525755450218643496>"
                )
                # embed confirmation message
                em = discord.Embed(description=reward_msg, colour=0x607D4A)
                em.set_thumbnail(url=pet_avatar)
                await context.send(embed=em)
                return

            # 1. use the index of lowest gear item acquired above
            # 2. upgrade that minimum stat by 1
            if index_smallest == 0:
                reward_msg += f"Upgraded to level **{weapon_level + 1}** <:weapon1:532252764097740861>"
                pet_owner.update_user_battle_gear("weapon", weapon_level + 1)
            elif index_smallest == 1:
                reward_msg += f" Upgraded to level **{helmet_level + 1}** <:helmet2:532252796255469588>"
                pet_owner.update_user_battle_gear("helmet", helmet_level + 1)
            elif index_smallest == 2:
                reward_msg += f"Upgraded to level **{chest_level + 1}** <:chest5:532255708679503873>"
                pet_owner.update_user_battle_gear("chest", chest_level + 1)
            else:
                reward_msg += f"Upgraded to level **{boots_level + 1}** <:boots1:532252814953676807>"
                pet_owner.update_user_battle_gear("boots", boots_level + 1)

            reward_msg += " <a:worryHype:487059927731273739>"

        # embed confirmation message
        em = discord.Embed(description=reward_msg, colour=0x607D4A)
        em.set_thumbnail(url=pet_avatar)
        await context.send(embed=em)

    """PET PROFILE PAGE FUNCTION"""

    @has_account()
    @has_pet()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="pet", description="check your pet status", brief="can use =pet", aliases=["PET", "Pet"],
    )
    async def pet_profile(self, context):
        # create instance of the user who wishes to view their pet stats
        pet_owner = Users(context.author.id)
        # retrieve pet name
        pet_name = pet_owner.get_user_pet_name()
        # retrieve integer of pet's current xp
        pet_xp = pet_owner.get_user_pet_xp(0)
        # retrieve integer of pet's current level
        pet_level = pet_owner.get_user_pet_level(0)

        # calculate the current XP level up requirement for the user's pet
        level_up_cost = int(300 * ((pet_level + 1) ** 1.18) - (300 * pet_level))

        if pet_level == 1:
            pet_avatar = "https://cdn.discordapp.com/emojis/563872560308289536.png?v=1"
            hunt_gear_chance = "10%"
        elif pet_level == 2:
            pet_avatar = "https://cdn.discordapp.com/emojis/491930617823494147.png?v=1"
            hunt_gear_chance = "13%"
        elif pet_level == 3:
            pet_avatar = "https://cdn.discordapp.com/emojis/435032643772350464.png?v=1"
            hunt_gear_chance = "15%"
        elif pet_level == 4:
            pet_avatar = "https://cdn.discordapp.com/emojis/400690504104148992.png?v=1"
            hunt_gear_chance = "17%"
        else:
            pet_avatar = "https://cdn.discordapp.com/emojis/422845006232027147.png?v=1"
            hunt_gear_chance = "20%"

        pet_details = (
            f"**{pet_name}** (Pet Profile) \n\n**XP:** {pet_xp}/{level_up_cost}\n**Level:** {pet_level}"
            f"\n\n_Chance for gear upgrade while hunting: {hunt_gear_chance}_"
        )

        # embed pet's details into a message
        em = discord.Embed(description=pet_details, colour=0x607D4A)
        em.set_thumbnail(url=pet_avatar)
        await context.send(embed=em)

    """PET PROFILE PAGE FUNCTION"""

    @has_account()
    @has_pet()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(
        name="petname", description="change your pet name", brief="can use =petname", aliases=["petalias"],
    )
    async def update_pet_name(self, context):
        # create instance of the user who wishes to change their pet name
        pet_owner = Users(context.author.id)
        # retrieve pet name
        pet_name = pet_owner.get_user_pet_name()

        intro_msg = f"Welcome to the **Pet Shelter**!\n\nPlease enter your new name for **{pet_name}** now:"
        # embed intro message, then overwrite the variable with the actual message object
        em = discord.Embed(description=intro_msg, colour=0x607D4A)
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/560065150489722880.png?size=128")
        await context.send(embed=em)

        # wait for user's pet name entry
        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        pet_name = await self.client.wait_for("message", check=is_author, timeout=60)
        # remove everything except alphanumerics from the user's pet name entry
        pet_name = re.sub(r"\W+", "", pet_name.clean_content)

        # create an object to scan profanity
        pf = ProfanityFilter()
        # while the pet name entry has profanity, prompt user to re-enter a name
        while not pf.is_clean(pet_name):
            await context.send("Pet name has profanity! Please enter a new one now:")
            # wait for user's new pet name entry
            pet_name = await self.client.wait_for("message", check=is_author, timeout=60)
            # remove everything except alphanumerics from the user's pet name entry
            pet_name = re.sub(r"\W+", "", pet_name.clean_content)

        confirmation_msg = pet_owner.update_user_pet_name(pet_name[:15])
        # embed confirmation message
        em = discord.Embed(description=confirmation_msg, colour=0x607D4A)
        em.set_thumbnail(url="https://cdn.discordapp.com/emojis/746904102650249296.gif?v=1")
        await context.send(embed=em)


def setup(client):
    client.add_cog(Pets(client))
