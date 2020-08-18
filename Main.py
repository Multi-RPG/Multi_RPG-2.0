#!/usr/bin/env python3
import discord
import asyncio
import configparser
import sys
import datetime
import logging

from discord.ext import commands
from pathlib import Path
from Database import Database
from parse_args import parse_args

# Bot's prefix is defaulted to '='.
bot_prefix = "="

# Command error handling
enable_error = True

# Parse command-line for custom settings, such as changing the default prefix and enabling the dev mode to enable
# error messages.
args = parse_args()
if args.dev:
    bot_prefix = "."
    enable_error = False
    print(f"Running dev mode. enable_error = {enable_error}")

# Check if a prefix was passed, so we override the prefix set by args.dev
if args.prefix:
    bot_prefix = args.prefix

client = commands.Bot(command_prefix=[bot_prefix])
print(f"Prefix set to [{bot_prefix}]")

# remove the default help command
client.remove_command("help")

# set up logging for command errors
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler = logging.FileHandler("logs/commands_errors.txt")
handler.setFormatter(formatter)

commands_logger = logging.getLogger("commands_logger")
commands_logger.setLevel(logging.INFO)
commands_logger.addHandler(handler)


@client.event
async def on_ready():
    print(f"Logged in as {client.user.name}\n{client.user.id}\n---------")
    await client.change_presence(activity=discord.Game(name="=help for commands"))


@client.event
async def on_message(message):
    # when we don't want the bot to reply to itself
    if message.author == client.user:
        return

    # need this statement for bot to recognize commands
    await client.process_commands(message)


@client.command(
    name="help", description="command information", brief="commands", aliases=["h", "HELP"],
)
async def helper(context):
    # using discord's "ml" language coloring scheme for the encoded help message
    msg = (
        "```ml\n"
        "Utilities:\n"
        '  =clear          use "=clear" or "=clear X", -- X being #  messages \n'
        '  =code           use "=code" to view this bot\'s source code\n'
        '  =invite         use "=invite" to view the bot\'s invitation link\n'
        '  =id             use "=id" to view your personal discord ID\n'
        '  =remindme       use "=remindme "message" X"  -- X being the timer\n'
        "Account:\n"
        '  =create         use "=create" to make a account\n'
        '  =daily          use "=daily" for free money equal to 60x your level\n'
        '  =daily2         use "=daily2" for free money equal to 50x your level\n'
        '  =shop           use "=shop" to view the daily shop items\n'
        '  =buy            use "=buy X" to purchase shop item  -- X being item #\n'
        '  =levelup        use "=levelup" to level up your account\n'
        "                  (this results in higher profits & battle successes)\n\n"
        '  =ranks          use "=ranks" or "=leaderboards" to view top 15 battlers\n'
        '  =profile        use "=profile" or "=profile @user" to print battle & gear stats\n'
        '  =level          use "=level" or "=level @user" to print account level\n'
        '  =money          use "=money" or "=money @user" to print bank balance\n'
        '  =give           use "=give @user X" -- X being money to give a user\n```'
    )
    msg2 = (
        "```ml\n"
        "Games For Money:\n"
        '  =lotto          use "=lotto" for a 1/5 chance to win 100x your level each day\n'
        '  =lotto2         use "=lotto2" for a 1/5 chance to win 170x your level each day\n'
        '  =tourney        use "=tourney" to compete in a server-based, daily FFA tournament\n'
        "                  NOTE: this event takes item level & user level into calculation\n"
        "                  NOTE: this event requires AT LEAST 2 entries from your server\n"
        "                  NOTE: the reward is 170x your level for first, 100x for second\n"
        '  =rob            use "=rob" for a 7/10 chance to mug a random player\n'
        '  =rob            use "=rob @user" for a 6.5/10 chance to mug a specified player\n'
        '  =fight          use "=fight @user X" -- X being money to bet\n'
        '  =flip           use "=flip" or "=flip X" or "=flip X Y" \n'
        "                  -- X being heads or tails guess\n"
        "                  -- Y being amount to bet\n"
        '  =slots          use "=slots" to roll the slot machine for $10! (up to 15x a day)\n'
        '  =slothelp       use "=slothelp" for information on rewards calculation\n'
        '  =cards          use "=cards" to play High and Low game. You and your opponent get 3 cards\n'
        "                  try to guess if the sum of your cards is higher or lower than your opponent's\n"
        '  =hangman        use "=hangman" or "=hangman X", -- X being a category number \n'
        '                  use "=hm cats" for category numbers\n'
        '                  use "stop" or "cancel" to stop game\n'
        "                  NOTE: the reward is 8x your level\n"
        "Pets:\n"
        '  =adopt          use "=adopt" to adopt your own pet to reap more rewards\n'
        '  =feed           use "=feed" to gain pet XP, to earn better chance for rewards\n'
        '  =hunt           use "=hunt" to either gain gold or a gear upgrade\n'
        '  =pet            use "=pet" to display statistics for your pet```'
    )
    msg3 = (
        "```ml\n"
        "Meme Maker:  \n"
        "  =custom         =custom to create a custom Twitter-style meme \n"
        '  =changemymind   =changemymind "opinion" \n'
        '  =pigeon         =pigeon "boy" "butterfly" "is this a pidgeon?" \n'
        '  =boyfriend      =boyfriend "new girl" "distracted boyfriend" "girlfriend"\n'
        '  =brain          =brain "stage1" "stage2" "stage3" "stage4"\n'
        '  =twobuttons     =twobuttons "option 1" "option2"\n'
        '  =slapbutton     =slapbutton "cause" "reaction"\n'
        '  =leftexit       =leftexit "left" "right" "car"\n'
        '  =trumporder     =trumporder "order"\n'
        '  =reasonstolive  =reasonstolive "reasons"\n'
        '  =bookfacts      =bookfacts "facts"\n\n\n'
        "Server Toggles:  \n"
        '  =toggleannouncements    use "=toggleannouncements" to toggle the daily announcements for your server\n'
        "                          NOTE: this command requires Administrator privilege for your server\n"
        "User Toggles:  \n"
        '  =togglepeace            use "=togglepeace" to toggle rob target peace mode for yourself \n'
        "                          NOTE: this toggle disables =rob @user for yourself and people targetting you\n"
        "                          NOTE: peace mode has a cooldown that only resets once every week on Monday```"
    )
    msg4 = "```ml\n" "https://discord.gg/BGAwXft" "```"

    # Person that invoked this command.
    author = context.author

    try:
        await author.create_dm()
        await author.dm_channel.send(msg)
        await author.dm_channel.send(msg2)
        await author.dm_channel.send(msg3)
        await author.dm_channel.send(msg4)
    except discord.Forbidden as error:
        print(f"{type(error).__name__} {error.text}")
        error_msg = (
            f"I was unable to DM you the help message. "
            f"It is possible that you do not allow DM from server members. "
            f"Please check your privacy settings."
        )
        await context.send(error_msg)


@client.command(
    name="toggleannouncements",
    description="use to toggle daily announcements",
    brief="toggle server announcements",
    aliases=["announcements", "ANNOUNCEMENTS", "TOGGLE", "TOGGLEANNOUNCEMENTS"],
)
async def announcements_toggle(context):
    # connect to database through our custom Database module
    db = Database(0)
    db.connect()

    # if the server id does not exist in our database, insert it
    if db.find_server(context.guild.id) == 0:
        db.insert_server(context.guild.id)

    # if the user has admin privileges, permit them to toggle the daily server announcements
    if context.author.guild_permissions.administrator:
        # flip the status and retrieve the new announcements status
        new_status = db.toggle_server_announcements(context.guild.id)

        # if the new status is off, they just toggled off the announcements
        if new_status == 0:
            result_str = (
                "<a:worrycry:525209793405648896> Turned **off** daily server announcements"
                " <a:worrycry:525209793405648896>\nAwards will still be distributed daily."
            )
            # embed the confirmation into a message and send
            em = discord.Embed(description=result_str, colour=0x607D4A)
            thumb_url = "https://cdn.discordapp.com/icons/{0.id}/{0.icon}.webp?size=40".format(context.guild)
            em.set_thumbnail(url=thumb_url)
            await context.send(embed=em)
        # if the new status is on, they just toggled on announcements
        else:
            result_str = (
                "<a:worryblow:535914005244411904> Turned **on** daily server announcements!"
                " <a:worryblow:535914005244411904>"
            )
            # embed the confirmation into a message and send
            em = discord.Embed(description=result_str, colour=0x607D4A)
            thumb_url = "https://cdn.discordapp.com/icons/{0.id}/{0.icon}.webp?size=32".format(context.guild)
            em.set_thumbnail(url=thumb_url)
            await context.send(embed=em)
    # else inform the user they lack sufficient privileges
    else:
        await context.send("You need a local server administrator to do that!")


# Commands error handling
if enable_error:

    @client.event
    async def on_command_error(context, error):
        if isinstance(error, commands.CommandOnCooldown):
            # error.retry_after returns float, need to cast to integer without decimals
            # now convert to proper HH:MM:SS format and print the cooldown
            time = str(datetime.timedelta(seconds=int(error.retry_after)))
            msg = f"You are on cooldown: {time}"
            await context.send(msg)

        elif isinstance(error, commands.CommandNotFound):
            error_msg = await context.send("Command not found...")
            await asyncio.sleep(10)
            await context.message.delete()
            await error_msg.delete()
            commands_logger.info(f"{str(error)}\nInitiated by: {context.author.name}, ID: {context.author.id}")

        # we use command checks when checking if user voted within 12 hours,
        # or if a user has a pet/account in the database
        elif isinstance(error, commands.CheckFailure):
            # if the check failed for the daily2 function in Account.py
            if "daily2" in str(error):
                error_msg = (
                    "Failed! You have not voted within the last 12 hours."
                    "\nhttps://discordbots.org/bot/486349031224639488/vote"
                )
                em = discord.Embed(title=context.author.display_name, description=error_msg, colour=0x607D4A,)
                em.set_thumbnail(url="https://cdn.discordapp.com/emojis/440598341877891083.png?size=64")
                await context.send(embed=em)
            # if the check failed for one of the 3 pet interaction functions in Pets.py
            elif any(x in str(error) for x in ["feed", "hunt", "pet"]):
                error_msg = "Failed! You have no pet! Use **=adopt** to adopt a pet."
                em = discord.Embed(title=context.author.display_name, description=error_msg, colour=0x607D4A,)
                em.set_thumbnail(url="https://cdn.discordapp.com/emojis/440598341877891083.png?size=64")
                await context.send(embed=em)
            else:
                await context.send(" No account found.\nUse **=create** to make one.")

        # if the error fell in none of the above, log the error in our commands_errors.txt file
        else:
            error_message = (
                f"{str(error)} in command: {str(context.command)}, \n"
                f"User tried: {str(context.message.clean_content)}\n"
                f"Initiated by: {context.author.name} ID: {context.author.id}."
            )
            commands_logger.info(error_message)

        # special cases
        # if permissions/access error is indicated from discord's response string, private message the user
        if "Permissions" in str(error):
            await context.send(
                "I couldn't talk to you in there!\n"
                "I am likely missing **permissions**"
                " to communicate in that channel.",
            )
            await context.send(str(error))
        elif "Access" in str(error):
            await context.send("I couldn't talk to you in there!\n" "I am likely missing **access** to that channel.",)
            await context.send(str(error))


"""
        "Games",
"""

if __name__ == "__main__":
    for extension in [
        "Account",
        "DiscordBotsOrgApi",
        "Utilities",
        "Pets",
        "Shop",
        "Lottery",
        "Memes",
    ]:
        try:
            client.load_extension(extension)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("Failed to load extension {}\n{}".format(extension, exc))

# set up parser to config through our .ini file with our bot's token
config = configparser.ConfigParser()
bot_token_path = Path("tokens/tokenbot.ini")  # use forward slash "/" for path directories
# confirm the token is located in the above path
if bot_token_path.is_file():
    config.read(bot_token_path)
    # we now have the bot's token
    TOKEN = config.get("BOT1", "token")
else:
    print(
        "\n", "Discord bot token not found at: ", bot_token_path, "... Please correct file path in Main.py file.",
    )
    sys.exit()

client.run(TOKEN)
