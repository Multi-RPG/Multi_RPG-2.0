#!/usr/bin/env python3

"""
The purpose of this script is to:
1. connect to database, and reset all "peace_cd" to 0 in "Users" table

PS: FOR FULL AUTOMATION, SCHEDULE THIS FILE TO RUN AUTOMATICALLY AT AN INTERVAL.
PS2: MAKE SURE TO CHANGE PATHS TO FULL FILE PATHS IF THIS IS AUTOMATED
"""


import sys

from Database import Database


def main():
    print("Weekly maintenance started...")

    # open database
    db = Database(0)
    db.connect()

    """ PERFORM WEEKLY PEACE COOLDOWN RESET """
    db.reset_peace_cooldowns()

    print("Done!")
    # end this weekly maintenance program
    sys.exit(0)


if __name__ == "__main__":
    main()
