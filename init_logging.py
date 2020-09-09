#!/usr/bin/env python3
import logging
import logging.handlers
import sys

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
LOG_FILE = "logs/multirpg_log.txt"


def get_console_handler(level):
    """set up console handler"""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    """set up file handler for commands error logging"""
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        backupCount=7,
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def init_logging(logger_name, level):
    """Set up logging for bot"""

    # set up logging for bot
    log = logging.getLogger(logger_name)
    log.setLevel(level)

    log.addHandler(get_console_handler(level))
    log.addHandler(get_file_handler())

    # Silence irrelevant loggers
    logging.getLogger("discord").setLevel(logging.ERROR)
    logging.getLogger("websockets").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)

    return log
