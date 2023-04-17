# -*- coding: utf-8 -*-
import logging
import os
from utils.console import Console
from utils.coloredlog import LOGLEVEL_SUCCESS, LOGLEVEL_DISABLE
CONSOLE = Console(colored=True)

# Some generic paths
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(CUR_DIR,"logs")

# Important game Paths
SETTINGS = os.path.join(CUR_DIR,"settings")
# ASSETS = os.path.join(CUR_DIR,"assets")

# IMAGES = os.path.join(ASSETS,"images")
# FONTS = os.path.join(ASSETS,"fonts")
# MAPS = os.path.join(ASSETS,"maps")
# MUSICS = os.path.join(ASSETS,"musics")
# SOUNDS = os.path.join(ASSETS,"sounds")

# Logging / Debuggin parameters
# Possible values for a log level using logging module: CRITICAL:50; ERROR:40; WARNING:30; INFO:20, DEBUG:10
# Possible values for a log level using CONSTANTS (can be adapted in init.py): LOGLEVEL_SUCCESS:15; LOGLEVEL_DISABLE:99999
LOGLEVEL_CONSOLE = logging.WARNING
LOGLEVEL_FILE = logging.DEBUG
LOGLEVEL_FILE = LOGLEVEL_DISABLE
LOG_FILE = "DYNAMIC"     #Sample: os.path.join(LOG_DIR,"logfile.log")  or "DYNAMIC" to have it generated with timestamp

if __name__ == "__main__":  
    CONSOLE.clear_screen()

    print(f"- CUR_DIR: '{CUR_DIR}'")
    print(f"- LOG_DIR: '{LOG_DIR}'")
    print(f"- SETTINGS: '{SETTINGS}'")