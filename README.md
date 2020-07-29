
# Multi_RPG-2.0
## About
Multi_RPG-2.0 is a new version of [Discord-Bot](https://github.com/jdkennedy45/Discord-Bot), written in python3.8, using discord.py v1.0.

## Features
 - Utility
 - Meme Makers
 - RPG elements
 - Games: Hangman, Slots, Lotto, many more.

## Run requirements:
1. Needs python 3.5.3+ with sqlite3, pillow, requests, discord (1.3.4), numpy, dblpy (info on discordbots.org), and profanityfilter packages installed (use python3 -m pip install X)
2. Optional: (Recommended) Create virtual environment, run `pip install -r requirements.txt`;
3. In `scripts/setup/` folder, run `python setup.py`
4. In new `tokens` folder, replace value in `tokenbot.ini` with your discord bot token
 
Optional entries in `tokens` folder:
 - imgflip account token in `tokenimgflip.ini` (if meme generation desired)
 - discordbots.org token in `token_dbo_api.ini` (if uploading statistics about your bot is desired)
 - google cloud service account, save as `creds.json` to upload database backups when `backup_script.py` is run
 
Optional edits in `db_and_words` folder:
 - list of discord "emojis" as `emoji_names.txt`, the emote ID's must be replaced for a different discord bot to use them

## Usage:
### Linux/macOS
```console
foo@bar:~$ python3 ./Main.py 
```
### Windows
```console
C:\Users\jsmith> python Main.py
```

Note: In this repository, paths are currently setup to run in a windows environment. Adjustment will need to be made for running on Unix.

## License
MIT - see LICENSE file
