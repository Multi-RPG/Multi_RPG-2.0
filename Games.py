#!/usr/bin/env python3
import random
import asyncio
import re
import discord
from discord.ext import commands
from Users import Users
from random import choices


def get_hangman_art():
    # prepare array of hangman art
    art_array = []
    with open("db_and_words\hangmen.txt") as my_file:
        for line in my_file:
            art_array.append(line)

    # convert respective list index-ranges to string with ''.join
    # the resulting art_array[0-6] will represent each stage of hangman
    art_array[0] = "".join(art_array[0:6])
    art_array[1] = "".join(art_array[7:13])
    art_array[2] = "".join(art_array[14:20])
    art_array[3] = "".join(art_array[21:27])
    art_array[4] = "".join(art_array[28:34])
    art_array[5] = "".join(art_array[35:41])
    art_array[6] = "".join(art_array[42:49])
    return art_array


def get_hangman_words():
    # only read words file once so we won't have to re-open the file every game call
    words_file = open("db_and_words\words.txt", "r")
    words = words_file.readlines()
    words_file.close()
    return words


def battle_decider(fighter1, fighter2, fighter1_weight, fighter2_weight):
    # choices function maps a selection to a probability, and selects one choice based off probability
    winner = choices([fighter1, fighter2], [fighter1_weight, fighter2_weight])
    print(winner)
    # choices function returning [1] or [2] so use regex to pull the integers out
    return int(re.findall(r"\d+", str(winner))[0])


def pick_word(cat):
    if cat == 1:
        random_word = random.choice(all_words[0:180])
        category = "Country name"
    elif cat == 2:
        random_word = random.choice(all_words[181:319])
        category = "Farm"
    elif cat == 3:
        random_word = random.choice(all_words[320:389])
        category = "Camping"
    elif cat == 4:
        random_word = random.choice(all_words[390:490])
        category = "Household items/devices"
    elif cat == 5:
        random_word = random.choice(all_words[491:603])
        category = "Beach"
    elif cat == 6:
        random_word = random.choice(all_words[604:648])
        category = "Holidays"
    elif cat == 7:
        random_word = random.choice(all_words[649:699])
        category = "US States"
    elif cat == 8:
        random_word = random.choice(all_words[700:998])
        category = "Sports & Hobbies"
    else:
        random_word = random.choice(all_words[649:699])
        category = "US States"

    # quick band-aid fix to truncate CR in text file, COMING BACK LATER TO FIX
    length = len(random_word) - 1  # to remove carriage return, I'm not using unix format to make the list
    random_word = random_word[:length]  # truncate word with [:length] cause of carriage return in text file...

    underscore_sequence = list("")  # this will be our list of underscores
    # it will be consistently replaced by guesses

    # fill the underscore_sequence list with underscore underscore_sequencelate of the correct word
    for x in random_word:
        if x == " ":
            underscore_sequence += "      "  # in the case of 2-word phrases, need to move everything over
        elif x == "'":
            underscore_sequence += " '"
        else:
            underscore_sequence += " \u2581"  # if not a space, add: \u2581, a special underscore character.
            # using to replace by correctly guessed letters

    return random_word.upper(), category, underscore_sequence


def add_guess_to_list(guess, guessed):  # accepts guess and list of all guesses
    if len(guess.clean_content) > 1:  # don't want to add whole word to guess list
        all_guessed = "".join(map(str, guessed))
        return guessed, all_guessed
    guessed.extend(guess.clean_content.upper())  # add last guess to the list of guessed words
    guessed.extend(" ")  # add space to guessed list
    all_guessed = "".join(map(str, guessed))  # messy syntax, convert the list into a string so bot can print it
    return guessed, all_guessed


def find_matches(guess, correct_word, underscore_sequence):
    index = 0
    num_matches = 0
    for x in correct_word:
        index += 1
        if x == " ":
            index += 2
        # if any matches, we need to replace underscore(s) in the sequence
        # and increase the number of matches for the loop
        if guess.clean_content.upper() == x:
            # convulted index scheme due to underscore_sequence format
            underscore_sequence[index * 2 - 1] = guess.clean_content.upper()
            num_matches += 1
    return num_matches, underscore_sequence


def get_slots_emoji_list():
    with open("db_and_words\\emoji_names.txt", "r") as lines:
        high_tier = []
        mid_tier = []
        low_tier = []

        current_tier = ""

        for line in lines:
            line = line.rstrip("\n")
            if line == "HIGH-TIER-LIST":
                current_tier = "high"
                continue
            if line == "MEDIUM-TIER-LIST":
                current_tier = "med"
                continue
            if line == "LOW-TIER-LIST":
                current_tier = "low"
                continue

            if current_tier == "high":
                high_tier.append(line)
            elif current_tier == "med":
                mid_tier.append(line)
            elif current_tier == "low":
                low_tier.append(line)
        return high_tier, mid_tier, low_tier


# short decorator function declaration, confirm that command user has an account in database
def has_account():
    def predicate(ctx):
        user = Users(ctx.author.id)
        if user.find_user() == 0:
            return False
        else:
            return True

    return commands.check(predicate)


# store data from text files into memory (emoji lists, hangman words, hangman art)
high_tier_emotes, mid_tier_emotes, low_tier_emotes = get_slots_emoji_list()
all_words = get_hangman_words()
hangmen = get_hangman_art()


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

    """ROB FUNCTION"""

    @has_account()
    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(
        name="rob",
        description="Steal money from others",
        brief="can use =steal",
        aliases=["thief", "thieve", "ROB", "steal", "mug"],
    )
    async def rob(self, context, *args):
        # create instance of the user starting the robbery
        robber = Users(context.author.id)
        # declare 30% fail chance, used to calculate chance of failing rob
        fail_chance = 30

        # if they specified a rob target, attempt to rob that target
        if args:
            try:
                # use regex to extract only the user-id from the user targeted
                victim_id = re.findall(r"\d+", args[0])[0]
                victim = Users(victim_id)

                # get_member() returns the "member" object that matches an id provided
                target = await context.guild.fetch_member(victim_id)

                # if the target doesn't have an account, change fail chance back to 30%
                # and the target will reroll next loop
                if victim.find_user() == 0 or victim_id == context.author.id:
                    await context.send(
                        f"{context.author.mention} Your target has no account or you attempted to rob yourself."
                        f"\n**Exiting now!**"
                    )
                    context.command.reset_cooldown(context)
                    return
                # if robber is in peace mode
                if robber.get_user_peace_status() == 1:
                    await context.send(
                        f"{context.author.mention} You are in :dove: **peace mode** :dove: and cannot specify a target!"
                    )
                    return
                # if target is in peace mode
                elif victim.get_user_peace_status() == 1:
                    await context.send(
                        f"{context.author.mention} That target is in :dove: **peace mode** :dove:. Try another target."
                    )
                    return
            except:
                context.command.reset_cooldown(context)
                await context.send(
                    f'{context.author.mention}```ml\nIf targeting with rob, use =rob like so: "=rob @User"'
                    f"\n(select an actual discord user after the @ sign, like you were to ping them)```"
                )
                return

        # if robber did not specify a target
        else:
            # pick a random user in the server to rob
            # target variable will function as the victim user's "english" name
            target = random.choice(list(context.guild.members))
            # make an instance of the target
            victim = Users(target.id)
            victim_id = target.id
            counter = 1

            # while the selected user to rob is the robber, re-roll the target
            # while the selected user to rob does not have an account in the database, re-roll the target
            while victim_id == context.author.id or victim.find_user() == 0:
                # only try 70 members in the user's server
                # otherwise if the user was the sole player with an account in the discord server, infinite while loop
                # this part is inefficient, but only way I can think of right now with discord's functionality
                if counter == 70:
                    no_targets_found_msg = f"**No users with Multi-RPG accounts found to rob...** \nExiting now..."
                    # embed the rob confirmation message, set thumbnail to 40x40 of a "ninja" gif
                    em = discord.Embed(description=no_targets_found_msg, colour=0x607D4A)
                    em.set_thumbnail(url="https://cdn.discordapp.com/emojis/618911376613834752.gif?size=40")
                    await context.send(embed=em)
                    context.command.reset_cooldown(context)
                    return
                target = random.choice(list(context.guild.members))
                # create a new instance of victim each loop
                # in order to check if the reroll has an account in database
                victim = Users(target.id)
                victim_id = target.id
                counter += 1

        # now that a target has been decided, roll dice to rob
        # calculate random integer 1-100
        # if the result is within 1 through fail chance, they failed the rob
        if fail_chance >= random.randint(1, 100) >= 1:
            rob_success = False
        else:
            rob_success = True

        # if robber successfully achieved a rob
        if rob_success:
            # we passed the dodge check, so reward thief with prize and bonus prize
            victim_money = victim.get_user_money(0)
            victim_level = victim.get_user_level(0)
            robber_level = robber.get_user_level(0)

            # the victim will only lose the prize, not the bonus prize
            bonus_prize = int(robber_level * 29.3)

            # the prize will begin by scaling by victim's level
            prize = int(victim_level * 9.4)
            # if prize greater than the robber's maximum prize amount, decrease the standard prize to compensate
            if prize > int(robber_level * 9.4):
                prize = int(robber_level * 9.4)
            # if prize less than the robber's maximum prize amount, increase the bonus prize to compensate
            if prize < int(robber_level * 9.4):
                bonus_prize += int(robber_level * 9.4 - prize)

            # balancing mechanic, don't let victims lose any more money when they have less money than -50x their level
            if not victim_money < (victim_level * -50):
                # subtract prize from victim
                victim.update_user_money(prize * -1)
            # reward robber with prize and bonus prize
            robber.update_user_money(prize + bonus_prize)

            success_msg = (
                f"**Success!** <:poggers:490322361891946496> \n"
                f"Robbed **${prize}** (+**${bonus_prize}**) from **{target.display_name}**"
            )

            # embed the rob confirmation message, set thumbnail to 40x40 of a "ninja" gif
            em = discord.Embed(description=success_msg, colour=0x607D4A)
            em.set_thumbnail(url="https://cdn.discordapp.com/emojis/419506568728543263.gif?size=40")
            await context.send(embed=em)

        # robber failed
        else:
            robber_level = robber.get_user_level(0)

            bail = int(robber_level * 10.4)
            robber.update_user_money(bail * -1)

            fail_msg = (
                f"<a:policesiren2:490326123549556746> :oncoming_police_car: "
                f"<a:policesiren2:490326123549556746>\n<a:monkacop:490323719063863306>"
                f"\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B"
                f"<a:monkacop:490323719063863306>\n**{target.display_name}** dodged"
                f" and the police shot you in the process.\nYou spent **${bail}** to bail out of jail."
            )

            # embed the rob failure message, set thumbnail to 80x80 of a "police siren" gif
            em = discord.Embed(description=fail_msg, colour=0x607D4A)
            em.set_thumbnail(url="https://cdn.discordapp.com/emojis/490326123549556746.gif?size=80")
            await context.send(embed=em)
            return

    """TOURNAMENT BATTLE FUNCTION"""

    @has_account()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="tournament", aliases=["TOURNAMENT", "tourney", "TOURNEY"],
    )
    async def enter_daily_tournament(self, context):
        # the bulk work of this feature is when the results are calculated from daily_maintenance.py
        # create instance of user who wants to enter the daily, server-specific colosseum tournament
        fighter = Users(context.author.id)
        # update their tourney_server_id entry to be the server they executed the command on
        msg = fighter.update_user_tourney_server_id(context.guild.name, context.guild.id)

        # embed the tourney registration confirmation message, set thumbnail to 40x40 of the respective server's icon
        em = discord.Embed(description=msg, colour=0x607D4A)
        thumb_url = "https://cdn.discordapp.com/icons/{context.guild.id}/{context.guild.icon}.webp?size=40"
        em.set_thumbnail(url=thumb_url)
        await context.send(embed=em)

    """1v1 BATTLE FUNCTION"""

    @has_account()
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(
        name="fight",
        description="Battle another user in your server",
        brief='can use "fight @user X --X being amount to bet"',
        aliases=["battle", "BATTLE", "FIGHT", "duel", "DUEL"],
    )
    async def battle_user(self, context, *args):
        # try/except block to check argument syntax
        try:
            if not args:
                msg = await context.send(
                    f"{context.author.mention}```ml\nuse =fight like so: "
                    f'"=fight @user X"  -- X being integer amount to bet```'
                )
                await asyncio.sleep(5)
                await msg.delete()
                return
            # retrieve how much the fighter is betting on the battle
            if len(args) == 2:
                # bet will always be second argument
                bet = int(args[1])
                if bet < 1:
                    await context.send("Bet can't be negative...")
                    return
            else:
                await context.send("No bet specified, defaulting to **$10**\n ** **")
                bet = 10
        # if the user still used syntax incorrectly
        except:
            await context.send(
                f"{context.author.mention}```ml\nuse =fight like so: "
                f'"=fight @user X"  -- X being integer amount to bet```'
            )

        # make instance of user for user initiating fight
        fighter1 = Users(context.author.id)

        # retrieve battle target
        target = args[0]
        # use regex to extract only the user-id from the user targeted
        fighter2_id = int(re.findall(r"\d+", target)[0])
        fighter2 = Users(fighter2_id)

        # check if targeted user has account
        if fighter2.find_user() == 0:
            await context.send(
                f"{context.author.mention} Your fighting target doesn't have an account."
                f"\nTell them to use **=create** to make one."
            )
            return

        # check if both users have enough money
        if fighter1.get_user_money(0) < bet or fighter2.get_user_money(0) < bet:
            await context.send(f"{context.author.mention} Either you or the target doesn't have enough money...")
            return

        # give target the prompt to ask if they will accept the challenge
        alert_msg = await context.send(
            f"{target}, you were challenged for **${bet}**\n"
            f":crossed_swords: Type **yes** to accept this battle. :crossed_swords: "
        )

        # made this check function with the help of discord API documentation
        # it will be called below to check if the confirmation response to fight is from fighter2
        def fighter2check(msg):
            return int(msg.author.id) == fighter2_id

        # (try to) wait for a battle acceptance from other user
        try:
            confirm = await self.client.wait_for("message", timeout=60, check=fighter2check)
            await alert_msg.delete()
            if confirm.clean_content.upper() == "YES":
                await confirm.delete()
                # have to use 2 messages to enlarge the emojis
                msg = f"{context.author.mention} vs {args[0]} for **${bet}**\nFight will conclude in 10 seconds..."
                # embed the duel alert message, set thumbnail to a "nunchuck frog" gif of size 64x64
                em = discord.Embed(title="", colour=0x607D4A)
                em.add_field(name="DUEL ALERT", value=msg, inline=True)
                em.set_thumbnail(url="https://cdn.discordapp.com/emojis/493220414206509056.gif?size=64")

                await context.send(embed=em)
                await asyncio.sleep(10)

                # get the stats of each fighter
                # algorithm for calculating a fighter's stats in duels: (item score + user level*2 + 20)
                f1_stats = fighter1.get_user_item_score() + (fighter1.get_user_level(0) * 2) + 20
                f2_stats = fighter2.get_user_item_score() + (fighter2.get_user_level(0) * 2) + 20
                total = f1_stats + f2_stats
                f1_weight = f1_stats / total
                f2_weight = f2_stats / total

                # decide winner with custom function
                # if it returns 1, fighter 1 won
                # if it returns 2, fighter 2 won
                winner = battle_decider(1, 2, f1_weight, f2_weight)

                # check if they tried to exploit the code by spending all their money during the battle
                if fighter1.get_user_money(0) < bet or fighter2.get_user_money(0) < bet:
                    await context.send(f"{context.author.mention} One of you spent money while battling...")
                    return

                # check who the winner was returned as
                # update account balances respectively
                if winner == 1:
                    msg = f"{context.author.mention} won **${bet}** by defeating {target}"
                    # embed the duel results message
                    em = discord.Embed(description=msg, colour=0x607D4A)
                    await context.send(embed=em)

                    # distribute money properly
                    fighter1.update_user_money(bet)
                    fighter2.update_user_money(bet * -1)

                elif winner == 2:
                    msg = f"{target} won **${bet}** by defeating {context.author.mention}"
                    # embed the duel results message
                    em = discord.Embed(description=msg, colour=0x607D4A)
                    await context.send(embed=em)

                    # distribute money properly
                    fighter1.update_user_money(bet * -1)
                    fighter2.update_user_money(bet)

            else:
                await context.send(f"You rejected the battle! {target}")

        # if the target never responded
        except:
            await context.send("**Battle request ignored...** <a:pepehands:485869482602922021>")

    """FLIP COIN FUNCTION"""

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(
        name="flip",
        description="Flip a coin to earn social status.",
        brief='can use "=flip" or "=flip X", with X being heads or tails',
        aliases=["f", "flpi", "FLIP", "F"],
    )
    async def flip_coin(self, context, *args):
        result = random.randint(0, 1)  # flipping in "binary"
        win = 0

        # first, check if they specified a bet and they have enough money for it
        # this try/catch block will simply pass if they did not specify a bet
        try:
            user = Users(context.author.id)

            # Convenient way to flip all
            if type(args[1]) == str and args[1] == "all":
                bet = user.get_user_money(0)
            else:
                bet = int(args[1])

            # pass 0 to return integer version of money, see USERS.PY function
            if bet > user.get_user_money(0) or bet < 1:
                error_msg = await context.send(
                    f"You don't have enough money for that bet..."
                    f" <a:pepehands:485869482602922021> {context.author.mention}"
                )
                await asyncio.sleep(6)
                await error_msg.delete()

                return
        except:
            pass

        gif = await context.send(
            "https://media1.tenor.com/images/938e1fc4fcf2e136855fd0e83b1e8a5f/tenor.gif?itemid=5017733"
        )
        await asyncio.sleep(3)
        await gif.delete()

        # check if they specified a guess of heads or tails
        # process if they won or not
        try:
            if args[0] in ["heads", "HEADS"]:
                if result == 1:
                    msg = "<:heads:486705167643967508> Result is **Heads**! You win! <a:worryHype:487059927731273739>"
                    win = 1
                else:
                    msg = "<:heads:486705184370589718> Result is **Tails**! You lost. <a:pepehands:485869482602922021>"
            elif args[0] in ["tails", "TAILS"]:
                if result == 1:
                    msg = "<:heads:486705167643967508> Result is **Heads**! You lost. <a:pepehands:485869482602922021>"
                else:
                    msg = "<:heads:486705184370589718> Result is **Tails**! You win! <a:worryHype:487059927731273739>"
                    win = 1
            else:
                error_msg = await context.send("Did you mean heads or tails? Try **=flip heads** or **=flip tails**.")
                await asyncio.sleep(6)
                await error_msg.delete()
                return
        except:
            # no arguments provided at all. so just give a result
            if result == 1:
                msg = "<:heads:486705167643967508> Result is **Heads**!"
            else:
                msg = "<:heads:486705184370589718> Result is **Tails**!"

        # if they specified a "guess" and "bet" that was valid, check if they won
        # note this will only pass through if "bet" was assigned through the earlier try/catch
        try:
            if win == 1:
                # triple user's bet if they win, add to account
                msg2 = f"\n{user.update_user_money(bet)}"
            else:
                # remove user's bet from their account if they lose
                msg2 = f"\n{user.update_user_money(bet * -1)}"
                # if they have $0 after that flip, give a donation dollar to discourage account re-creation
                # pass in 0 for get_user_money to return the money as integer, SEE USERS.PY
                if user.get_user_money(0) == 0:
                    msg2 += "\n** **\n_Mission failed. We'll get 'em next time. Take this **$1**._"
                    msg2 += f"\n{user.update_user_money(1)}"
        except:
            pass

        try:
            # embed the flip results message with money won and send
            em = discord.Embed(description=msg + msg2, colour=0x607D4A)
            await context.send(context.author.mention, embed=em)
        except:
            # embed the flip results message and send
            em = discord.Embed(description=msg, colour=0x607D4A)
            await context.send(context.author.mention, embed=em)

    """HANGMAN main function"""

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(
        name="hangman",
        description="Guess the word in order to survive.",
        brief='can use "=hangman", type "stop" or "cancel" to end game',
        aliases=["hm", "hang", "HM", "HANGMAN"],
    )
    async def hangman(self, context, *args):
        # initialize message to be printed if user wants category list
        hm_help = (
            "```fix\n1. Country name\n2. Farm\n3. Camping\n4. Household items/devices\n"
            "5. Beach\n6. Holidays\n7. US States\n8. Sports & Hobbies```"
        )
        wrong_guesses = 0  # global running count of incorrect guesses
        guessed_letters = [""]  # string of letters

        # pick starting word with a category, also make the string of underscores to replace later
        # check if they want to list the categories
        if args:
            if args[0] in ("help", "HELP", "categories", "cats", "h"):
                await context.send(f"{context.author.mention} Categories:\n{hm_help}")
                return
            try:
                correct_word, category, underscore_sequence = pick_word(int(args[0]))
            except:
                await context.send("Use a category number! (**Ex for Beach**: =hm 5)")
                return
        # if no category was specified in argument by user...
        else:
            # pick random category 1-8
            rand_category = random.randint(1, 8)
            correct_word, category, underscore_sequence = pick_word(rand_category)

        # print the hangman starting interface and ascii setup
        # use ** ** for empty line, discord doesn't allow empty messages.
        # also, using "".join because discord api can't  print lists.
        # we could cast, but the format would be unfriendly for the game.
        cat_msg = await context.send(f"{context.author.mention} Word category is: **```fix\n{category}\n```**")
        art_msg = await context.send(f"\n** **\n{hangmen[0]}\n** **\n{''.join(underscore_sequence)}")

        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        counter = 0
        while True:  # main game loop
            guess_prompt_msg = await context.send("*Guess a letter or the entire word now...*")
            guess_msg = await self.client.wait_for("message", check=is_author, timeout=60)  # wait for user's guess_msg

            # make already_guessed boolean to facilitate a while loop that will loop if the user makes duplicate guess
            already_guessed = 1
            while already_guessed == 1:  # loop that will exit immediately if letter guess_msg isn't a repeat
                if guess_msg.clean_content.upper() in str("".join(guessed_letters)):
                    await guess_msg.delete()
                    already_guessed_msg = await context.send(
                        "\n*You already tried that. Guess a different letter now...*"
                    )
                    # wait for user's guess_msg now
                    guess_msg = await self.client.wait_for("message", check=is_author, timeout=30)
                    await already_guessed_msg.delete()
                else:
                    already_guessed = 0

            """RUN WIN CHECKS AND CANCEL CHECKS NOW"""
            # run conditionals to check if they guessed entire word or they used a cancel keyword
            print(f"{guess_msg.clean_content.upper()} and correct word: {correct_word}")  # console print
            if guess_msg.clean_content.upper() == correct_word:
                await cat_msg.delete()
                await art_msg.delete()
                await guess_prompt_msg.delete()
                await guess_msg.delete()
                # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
                if counter > 0:
                    await pick_result_msg.delete()
                    await underscore_seq_msg.delete()
                    await guessed_list_msg.delete()
                await context.send(hangmen[wrong_guesses])
                # prepare win message string & embed it
                win_msg = (
                    f"**Correct word pick** <a:worryHype:487059927731273739>"
                    f" Correct word was: **{correct_word.upper()}**\n"
                )
                # add WINNINGS to user's bank account now
                user = Users(context.author.id)
                prize = user.get_user_level(0) * 10
                win_msg += f"Won **${prize}**... {user.update_user_money(prize)}"
                em = discord.Embed(description=win_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return

            if guess_msg.clean_content.upper() in ["STOP", "CANCEL"]:
                await cat_msg.delete()
                await art_msg.delete()
                await guess_prompt_msg.delete()
                await guess_msg.delete()
                # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
                if counter > 0:
                    await pick_result_msg.delete()
                    await underscore_seq_msg.delete()
                    await guessed_list_msg.delete()
                await context.send(
                    f"**Cancelled** the game!! <a:pepehands:485869482602922021> "
                    f"Correct word was: **{correct_word.upper()}** {context.author.mention}"
                )
                return

            # quick win check, check for any underscores left to fill.
            # if unknown_letters ends up as 0 for this iteration, then there are no letters left to guess.
            num_matches, underscore_sequence = find_matches(guess_msg, correct_word, underscore_sequence)
            unknown_letters = 0
            for x in underscore_sequence:
                if x == "\u2581":  # if there is a blank underscore , the letter is still unknown to the user
                    unknown_letters += 1
            if unknown_letters == 0:
                await cat_msg.delete()
                await art_msg.delete()
                await guess_prompt_msg.delete()
                await guess_msg.delete()
                # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
                if counter > 0:
                    await pick_result_msg.delete()
                    await underscore_seq_msg.delete()
                    await guessed_list_msg.delete()
                await context.send(hangmen[wrong_guesses])
                # prepare win message string & embed it
                win_msg = (
                    f"You **won** the game!! <a:worryHype:487059927731273739> "
                    f"Correct word was: **{correct_word.upper()}**\n"
                )
                # add WINNINGS to user's bank account now
                user = Users(context.author.id)
                prize = user.get_user_level(0) * 10
                win_msg += f"Won **${prize}**... {user.update_user_money(prize)}"
                em = discord.Embed(description=win_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return

            # now clear all messages besides category message (cat_msg variable)
            await art_msg.delete()
            await guess_prompt_msg.delete()
            await guess_msg.delete()
            # pick_result_msg, underscore_seq_msg, guessed_list_msg will only exist if the game has gone at least 1 loop
            if counter > 0:
                await pick_result_msg.delete()
                await underscore_seq_msg.delete()
                await guessed_list_msg.delete()

            # if user's guess has zero matches in the correct word
            if num_matches == 0:
                wrong_guesses += 1  # no letters matched, so they guessed a wrong letter
                if len(guess_msg.clean_content) == 1:
                    pick_result_msg = await context.send("**Wrong letter pick** <a:pepehands:485869482602922021>")
                else:
                    pick_result_msg = await context.send("**Wrong word pick** <a:pepehands:485869482602922021>")
            # if user's guess has any matches found in the correct word
            else:
                pick_result_msg = await context.send("**Correct letter pick** <a:worryHype:487059927731273739>")
                # don't need "correct word pick" next because that would trigger
                # in the conditional right after the guess is taken

            # print the ascii art corresponding to wrong guesses
            if wrong_guesses < 6:
                art_msg = await context.send(hangmen[wrong_guesses])
            elif wrong_guesses == 6:
                await cat_msg.delete()
                await pick_result_msg.delete()
                await context.send(hangmen[6])
                losing_msg = (
                    f"\nYou were **hanged**! <a:pepehands:485869482602922021> The word was: **{correct_word}**\n"
                )
                em = discord.Embed(description=losing_msg, colour=0x607D4A)
                await context.send(context.author.mention, embed=em)
                return

            # print underscores/letters, our main interface
            underscore_seq_msg = await context.send(f"** **\n**{''.join(underscore_sequence)}**")
            # add last guessed letter to our guessed-so-far list
            guessed_letters, all_guessed = add_guess_to_list(guess_msg, guessed_letters)
            # print all letters guessed so far
            guessed_list_msg = await context.send(f"** ```fix\nGuessed so far: {all_guessed}``` **")
            # add 1 to the main game loop's counter
            counter += 1

    """ Slot Machine """

    @has_account()
    @commands.cooldown(15, 86400, commands.BucketType.user)
    @commands.command(
        name="slot", description="Slot Machine game", aliases=["machine", "pachinko", "slots", "spin", "reel"],
    )
    async def slot_machine(self, context):

        # Create a user instance
        user = Users(context.author.id)

        # Check if user has enough money. Ticket costs $10
        ticket_cost = 10
        if user.get_user_money(0) < ticket_cost:
            msg = await context.send(
                f"{context.author.mention} You don't have enough money...\n ticket_cost costs ${ticket_cost}!"
            )
            await asyncio.sleep(5)
            await msg.delete()
            return

        # Deduct ticket cost from user
        user.update_user_money(ticket_cost * -1)

        # High tier should have the lowest chance possible
        def get_tier():
            """ High tier => 7%
                Mid Tier => 28%
                Low Tier => 65%
            """
            tier = ""
            # Scuffed way to get real value
            # Get a random real value 0.01...100.0
            result = (random.randrange(1, 10001)) / 100
            if result <= 7.0:
                # High Tier
                tier = "high"
            elif result > 7.0 and result <= 35.0:
                # Mid Tier
                tier = "mid"
            elif result > 35.0 and result <= 100.0:
                # Low Tier
                tier = "low"
            return tier

        # This function and get_tier() can probably be merged
        def get_emoji(result):
            """Pick a emote from emote tier lists determined by the result
               Return a random emote
            """
            emote = ""
            if result == "high":
                emote = random.choice(high_tier_emotes)
            elif result == "mid":
                emote = random.choice(mid_tier_emotes)
            elif result == "low":
                emote = random.choice(low_tier_emotes)
            return emote

        def get_bonus(slot_machine):
            """Getting a jackpot gives user a reward = 500 + bonus
               Bonus is determined by the emote tier
               High tier = 2000.0
               Mid tier = 1000.0
               Low tier = 250.0

               Getting 2 same emotes also gives user a reward = 120 + bonus
               High tier = 230.0
               Mid tier = 130.0
               Low tier = 0.0

               If one emoji is high tier, user is given $50.0

               return a list with msg type, reward, and tier
               result[0] -> 1 if jackpot, 2 if two equal elements, 0 otherwise
               result[1] -> reward
               result[2] -> tier
            """
            # result list
            # default values incase of no bonus
            result = [0, 0, ""]

            # If all emojis are equal
            # Jackpot
            if len(set(slot_machine)) == 1:
                # Print Jackpot
                result[0] = 1
                if slot_machine[0] in high_tier_emotes:
                    result[1] = 500.0 + 2000.0
                    result[2] = "High"
                    return result
                elif slot_machine[0] in mid_tier_emotes:
                    result[1] = 500.0 + 1000.0
                    result[2] = "Mid"
                    return result
                elif slot_machine[0] in low_tier_emotes:
                    result[1] = 500.0 + 250.0
                    result[2] = "Low"
                    return result

            # If two emojis inside slot_machine are equal
            if len(set(slot_machine)) == 2:
                result[0] = 2
                temp = [i for i in slot_machine if slot_machine.count(i) > 1]
                if temp[0] in high_tier_emotes:
                    result[1] = 120.0 + 230.0
                    result[2] = "High"
                    return result
                elif temp[0] in mid_tier_emotes:
                    result[1] = 120.0 + 130.0
                    result[2] = "Mid"
                    return result
                elif temp[0] in low_tier_emotes:
                    result[1] = 120.0
                    result[2] = "Low"
                    return result

            # If one element is a High Tier emoji
            for i in slot_machine:
                if i in high_tier_emotes:
                    result[1] = 50.0
                    result[2] = "High"
                    return result

            return result

        # assign results to 3 different slots
        result_1 = get_tier()
        result_2 = get_tier()
        result_3 = get_tier()

        # Get emotes from  the tier lists.
        slot_1 = get_emoji(result_1)
        slot_2 = get_emoji(result_2)
        slot_3 = get_emoji(result_3)

        # Check for bonus
        slot_machine = [slot_1, slot_2, slot_3]
        bonus = get_bonus(slot_machine)
        # Update users balance
        user.update_user_money(bonus[1])

        result_msg = f"「 {slot_1}  {slot_2}  {slot_3} 」"

        # Jackpot worry image
        em1 = discord.Embed(title="", colour=0x801A06)
        em1.set_image(url="https://i.imgur.com/a9pARrC.gif")
        await context.send(embed=em1)
        await asyncio.sleep(1)

        # print result
        em2 = discord.Embed(title="", description=result_msg, colour=0x801A06)
        await context.send(embed=em2)
        # If bonus
        if bonus[1] != 0:
            # This assert only works in debug mode due to application error handling
            assert bonus[2] != ""  # Make sure there is an actual tier
            if bonus[0] == 1:
                msg = f"**Jackpot**! <a:worrycash:525200274340577290>\n {bonus[2]} Tier! You won **${bonus[1]}**!"
            elif bonus[0] == 2:
                msg = f"You got **two** {bonus[2]} Tier! <a:worryHype:487059927731273739>\n You won **${bonus[1]}**!"
            elif bonus[1] == 50.0:
                msg = f"You got **one** {bonus[2]} Tier! <a:worryHype:487059927731273739>\n You won **${bonus[1]}**!"

            em3 = discord.Embed(title="", description=msg, colour=0xFFD700)
            await context.send(embed=em3)

    """ Slots tier list information """

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(
        name="tiers",
        description="Slot Machine help page",
        aliases=["slothelp", "slotshelp", "slottiers", "slotstiers"],
    )
    async def slot_tiers_help(self, context):
        msg = " ".join(high_tier_emotes)
        msg2 = " ".join(mid_tier_emotes)
        msg3 = " ".join(low_tier_emotes)
        msg4 = (
            "**3** Identical High tier = **$2,500**\n"
            "**3** Identical Mid tier = **$1,500**\n"
            "**3** Identical Low tier = **$750**\n\n"
            "**2** Identical High tier = **$350**\n"
            "**2** Identical Mid tier = **$250**\n"
            "**2** Identical Low tier = **$120**\n\n"
            "**1** of __any__ High tier = **$50**"
        )

        try:
            await context.author.create_dm()

            em = discord.Embed(title="**High-tier emotes**", description=msg, colour=0xFFD700)
            await context.author.dm_channel.send(embed=em)
            em = discord.Embed(title="**Mid-tier emotes**", description=msg2, colour=0xFFD700)
            await context.author.dm_channel.send(embed=em)
            em = discord.Embed(title="**Low-tier emotes**", description=msg3, colour=0xFFD700)
            await context.author.dm_channel.send(embed=em)
            em = discord.Embed(title="**Rewards Information**", description=msg4, colour=0xFFD700)
            em.set_thumbnail(url="https://i.imgur.com/a9pARrC.gif")
            await context.author.dm_channel.send(embed=em)
        except discord.Forbidden as error:
            print(f"{type(error).__name__} {error.text}")
            error_msg = (
                f"I was unable to DM you the help message. "
                f"It is possible that you do not allow DM from server members. "
                f"Please check your privacy settings."
            )
            await context.send(error_msg)

    """ High and Low game """

    @has_account()
    @commands.cooldown(15, 86400, commands.BucketType.user)
    @commands.command(
        name="high_low",
        description="High and low game. Guess the sum of cards.",
        aliases=["hl", "guess", "cards", "card", "CARDS"],
    )
    async def high_and_low(self, context, *args):
        # try/except block to check argument syntax
        try:
            # there should be an argument
            if args:
                # retrieve bet as first argument
                bet = int(args[0])
                # if bet is negative, return
                if bet < 1:
                    await context.send("Bet can't be negative...")
                    return
            # if no argument provided
            else:
                await context.send(f"{context.author.mention}, no bet specified, defaulting to **$10** ** **")
                bet = 10
        except:
            await context.send(
                f'{context.author.mention}```ml\nuse =cards like so: "=cards X"  -- X being integer amount to bet```'
            )
            return

        # Create a user instance
        user = Users(context.author.id)

        # confirm the user has enough money for the bet
        if user.get_user_money(0) < bet:
            msg = f", you don't have enough money for that bet...\n"
            msg = await context.send(f"{context.author.mention}{msg}")
            await asyncio.sleep(7)
            await msg.delete()
            return

        CARDS = {
            0: "<:card_none:662372124748546058>",
            1: "<:card_one:662081420474449930>",
            2: "<:card_two:662373668214669313>",
            3: "<:card_three:662084754086166528>",
            4: "<:card_four:662085726493605918>",
            5: "<:card_five:662086717750247444>",
            6: "<:card_six:662088270993162253>",
            7: "<:card_seven:662091815087898649>",
            8: "<:card_eight:662455814543507456>",
            9: "<:card_nine:662092003676389380>",
        }

        instruction = "Three cards for you, three cards for me.\nYou flip one of yours over, and I flip two of mine."
        initial_hand = f"\n{CARDS[0]}  {CARDS[0]}  {CARDS[0]}\n{CARDS[0]}  {CARDS[0]}  {CARDS[0]}"
        em1 = discord.Embed(description=instruction + initial_hand, colour=0x607D4A)
        em1.set_thumbnail(url="https://cdn.discordapp.com/emojis/618921143163682816.png?v=1")
        msg1 = await context.send(embed=em1)
        cpu_cards, user_cards = get_cards()

        await asyncio.sleep(3)

        assert len(cpu_cards) == 3
        assert len(user_cards) == 3
        cpu_hand = f"{CARDS[cpu_cards[0]]}  {CARDS[cpu_cards[1]]}  {CARDS[0]}"
        user_hand = f"{CARDS[user_cards[0]]}  {CARDS[0]}  {CARDS[0]}"
        hand1 = f"Dealer's hand is: \u200B \u200B {cpu_hand}\nAnd your hand is: {user_hand}"
        instruction = (
            f"So, **{context.author.display_name}**, will your total be higher or lower than mine?"
            f"\n(*60 seconds to answer*)\n\n{hand1}\n\nEnter **low** or **high**..."
        )
        em2 = discord.Embed(description=instruction, colour=0x607D4A)
        em2.set_thumbnail(url="https://cdn.discordapp.com/emojis/618921143163682816.png?v=1")
        msg2 = await context.send(embed=em2)

        # helper to check if it's the author that it's responding.
        def is_author(m):
            return m.author == context.author and m.channel == context.channel

        # confirm the user's guess
        confirm = await self.client.wait_for("message", check=is_author, timeout=60)
        counter = 3
        if confirm:
            # while not a valid answer, keep prompting up to 3 times
            while confirm.clean_content.upper() != "HIGH" and confirm.clean_content.upper() != "LOW":
                if counter == 0:
                    await context.send("Sorry, you've reached your attempt limit. Exiting game.")
                    return
                if counter < 3:
                    await msg3.delete()
                    await msg4.delete()
                msg3 = await context.send("Wrong answer!")
                msg4 = await context.send(f"\nEnter **low** or **high**... You have **{counter}** more attempts.")
                confirm = await self.client.wait_for("message", check=is_author, timeout=60)
                counter -= 1

            cpu_hand = f"{CARDS[cpu_cards[0]]}  {CARDS[cpu_cards[1]]}  {CARDS[cpu_cards[2]]}"
            user_hand = f"{CARDS[user_cards[0]]}  {CARDS[user_cards[1]]}  {CARDS[user_cards[2]]}"

            hand2 = f"Dealer's hand is: \u200B \u200B {cpu_hand}\nAnd your hand is: {user_hand}"
            instruction2 = (
                f"You're going with **'{confirm.clean_content}'**, then, {confirm.author.display_name}.\n"
                f" Right, let's see what we've got...\n\n{hand2}"
            )

            # build embed of the hand results and send it
            em3 = discord.Embed(description=instruction2, colour=0x607D4A)
            em3.set_thumbnail(url="https://cdn.discordapp.com/emojis/618921143163682816.png?v=1")
            await context.send(embed=em3)

            # wait 2 seconds to build suspense
            await asyncio.sleep(2)

            won, sum_cpu, sum_user = win(cpu_cards, user_cards, confirm.clean_content.upper())
            results1 = f"My cards add up to **{sum_cpu}**.\nAnd you have a total of **{sum_user}**.\n\n"

            if won:
                winnings = get_reward(sum_cpu, sum_user, bet)
                update_user_money(user, winnings - bet, won)
                results2 = (
                    f"Congratulations, your guess was right!\nYou won **${winnings - bet}**. "
                    f"Your new account balance: {user.get_user_money()}."
                )
                em4 = discord.Embed(description=results1 + results2, colour=0x607D4A)
                em4.set_thumbnail(url="https://cdn.discordapp.com/emojis/525200274340577290.gif?size=64")
            else:
                # if the sums are the same, it's a draw.
                if is_same(sum_cpu, sum_user):
                    results2 = "Oh! It's a draw! Let's try again if you want!"
                    em4 = discord.Embed(description=results1 + results2, colour=0x607D4A)
                    # TODO: find an emoji for draw case.
                    em4.set_thumbnail(url="https://cdn.discordapp.com/emojis/525209793405648896.gif?size=64")
                # sums are not the same and user's hand isn't strong enough.
                else:
                    update_user_money(user, bet, won)
                    results2 = (
                        f"Aw... Sorry, but this match goes to me.\nYou lost **${bet}**. "
                        f"Your new account balance: {user.get_user_money()}"
                    )
                    em4 = discord.Embed(description=results1 + results2, colour=0x607D4A)
                    em4.set_thumbnail(url="https://cdn.discordapp.com/emojis/525209793405648896.gif?size=64")

            await context.send(embed=em4)
            await msg1.delete()
            await msg2.delete()

        # if we timed out waiting for user to answer
        else:
            await msg1.delete()
            await msg2.delete()
            await context.send("You didn't answer...")
            return


def handle_args(args):
    if args:
        # One arg: bet amount
        if len(args) == 1:
            return True, args[0]
        # We don't expect more than 2 args
        elif len(args) > 1:
            return False, None
    else:
        return False, None


def get_cards():
    cards = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    random.shuffle(cards)
    cpu_cards = cards[0:3]
    user_cards = cards[6:]
    return cpu_cards, user_cards


def win(cpu_hand, user_hand, user_guess):
    sum_cpu_hand = sum(cpu_hand)
    sum_user_hand = sum(user_hand)
    win = False
    if sum_user_hand > sum_cpu_hand and user_guess == "HIGH":
        win = True
    elif sum_user_hand < sum_cpu_hand and user_guess == "LOW":
        win = True
    return win, sum_cpu_hand, sum_user_hand


def is_same(sum_user, sum_cpu):
    return sum_user == sum_cpu


def get_reward(sum_cpu, sum_user, bet):
    diff = abs(sum_cpu - sum_user)
    return int(bet * 1.5) + diff


# update user's money if win or lose.
def update_user_money(user, amount, won):
    if won:
        user.update_user_money(amount)
    else:
        user.update_user_money(amount * -1)


def setup(client):
    client.add_cog(Games(client))
