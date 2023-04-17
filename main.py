# -*- coding: utf-8 -*-
__author__ = 'P. Saint-Amand'
__appname__ = 'Monsters'
__version__ = 'V 1.0.0'

# Standard Python Modules
import logging
import os
from pathlib import Path
from typing import Any

# External Python Modules
import pygame

# Personal Python Modules
from const import *
from game import Game
from utils.coloredlog import ColorLogger, get_logger, LOGLEVEL_SUCCESS, LOGLEVEL_DISABLE
from utils.filename import FileName

### Global Variables
### uncomment lines below if you want a dynamic log name instead
# LOGLEVEL_FILE = logging.DEBUG
if LOG_FILE == "DYNAMIC":
    LOG_FILE = os.path.join(LOG_DIR,__appname__+".log")
    logfilename_object = FileName(LOG_FILE)
    # logfilename_object.add_subname("subname")
    logfilename_object.add_datetime()
    LOG_FILE = logfilename_object.fullpath

def init():
    """ Clear Screen, display banner & start the logger. """
    CONSOLE.clear_screen()
    global logger
    logger = get_logger(logger_name=__appname__, console_loglevel=LOGLEVEL_CONSOLE, file_loglevel=LOGLEVEL_FILE, logfile=LOG_FILE, success_level=LOGLEVEL_SUCCESS)
    logger.info(f"Application Start")
    logger.info(f"Logging levels : Console={LOGLEVEL_CONSOLE}; File={LOGLEVEL_FILE}; Logfile='{LOG_FILE}'")
    logger.debug("Confirm Debug Mode is Activated")
    # logger.log(LOGLEVEL_SUCCESS, 'Then success level that is a custom level')

if __name__ == "__main__":
    init()
    game = Game(logger)
    game.pause_game(msg=game.title, enter_to_text="start")
    game.start_new_round()
    game.main_game_loop()