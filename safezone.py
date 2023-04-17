# Standard Python Modules
import os
from typing import Any

# External Python Modules
import pygame

# Personal Python Modules
from const import *
from utils.parameterfile import ParameterFile
from utils.coloredlog import ColorLogger


class SafeZone():
    def __init__(self, screen:pygame.Surface, logger:ColorLogger=None):
        self.logger = logger
        self.screen = screen
    
        # load Dashboard settings
        self.param_file = os.path.join(SETTINGS,"safezone.yaml")
        self.settings = ParameterFile(self.param_file, logger).parameters
        if self.logger:
            self.logger.info(f"SafeZone settings: {self.settings}")
        self._init_var_from_settings()
        
        # Determine Rectangle for Safe zone at BOTTOM of screen
        self.screen_rect = pygame.Rect(0, screen.get_height()-self.zone_height+1, screen.get_width(), self.zone_height)

        #Set font
        self.font = pygame.font.Font(self.font_path, size=self.font_size)

    def _init_var_from_settings(self):
        """ Initialize instance variables from setting file content """
        try:
            self.zone_height:str = self.settings["Height"]
            self.font_path:str = self.settings["Font"]["Path"]
            self.font_size:int = self.settings["Font"]["Size"]
            self.font_color:tuple = self.settings["Font"]["Color"]
            self.background_color:tuple = self.settings["Background"]["Color"]
        except Exception as e:
            if self.logger:
                self.logger.error(f"{str(e)} field not found in {self.param_file} !")
                self.logger.error(f"EXIT PROGRAM !!!")
            else:
                print("ERROR:", f"{str(e)} field not found in {self.param_file} !")
                print("ERROR:", f"EXIT PROGRAM !!!")
            exit()

    def draw(self):
        """Draw the Safezone"""
        text_margin = 10
        safezone_text = self.font.render("Safe Zone (press space to come here)", True, self.font_color )
        safezone_rect = safezone_text.get_rect()
        safezone_rect.centerx = self.screen_rect.centerx
        safezone_rect.top = self.screen_rect.top + text_margin

        #Blit the safe zone
        pygame.draw.rect(self.screen, self.background_color, self.screen_rect, 0)
        self.screen.blit(safezone_text, safezone_rect)

   

if __name__ == "__main__":
    pygame.init()
    safezone = SafeZone(screen=pygame.display.set_mode((1200, 600)))
                      