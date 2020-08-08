#! python3
import argparse


# Parse command-line arguments for the bot.
def parse_args():
    """
    Can set prefix and enable develop mode.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", help="Set a prefix for the bot.")
    parser.add_argument("-d", "--dev", help="Enable develop mode.", action="store_true")

    return parser.parse_args()
