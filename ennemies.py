# Standard Python Modules
import os
import random
from typing import Any

# External Python Modules
import pygame

# Personal Python Modules
from const import *
from utils.parameterfile import ParameterFile
from utils.coloredlog import ColorLogger

class Ennemies():
    """ A class with all the ennemies characteristics """
    def __init__(self, logger:ColorLogger=None):
        """Initialize the player"""
        # super().__init__()
        self.logger = logger

        # load list of ennemies & characteristics
        param_file = os.path.join(SETTINGS,"ennemies.yaml")
        self.ennemies_lst = ParameterFile(param_file, logger).parameters
        if self.logger:
            self.logger.info(f"Ennemies settings: {self.ennemies_lst}")

class Monster(pygame.sprite.Sprite):
    """A class to create enemy monster objects"""
    def __init__(self, settings:dict, play_zone:pygame.Rect, logger:ColorLogger=None):
        """Initialize the monster"""
        super().__init__()
        self.logger = logger
        self.screen_rect = play_zone
        self.settings = settings
        self._init_var_from_settings()

        # Initialize sound & image
        self.sound = pygame.mixer.Sound(file=self.sound_path_colllision)
        self.image = pygame.transform.scale(pygame.image.load(self.image_path), self.size)
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,0)

        # Set Random position in play_zone
        self.set_position((random.randint(self.screen_rect.left, self.screen_rect.right - self.size[0]), 
                            random.randint(self.screen_rect.top, self.screen_rect.bottom - self.size[1])))
        # Set random motion
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 1])
        self.velocity = random.randint(1, 5)

    def _init_var_from_settings(self):
        """ Initialize instance variables from setting file content """
        try:
            self.name:str = self.settings["Name"]
            self.sprite:bool = self.settings["Sprite"]
            self.image_path:str = self.settings["Image"]["Path"]
            self.size:tuple = self.settings["Image"]["Size"]
            self.color:tuple = self.settings["Image"]["Color"]
            self.sound_path_colllision:str = self.settings["Sound"]["Collision"]
        except Exception as e:
            if self.logger:
                self.logger.error(f"{str(e)} field not found in ennemies.yaml !")
                self.logger.error(f"EXIT PROGRAM !!!")
            else:
                print("ERROR:", f"{str(e)} field not found in ennemies.yaml !")
                print("ERROR:", f"EXIT PROGRAM !!!")
            exit()
            
    def update(self):
        """Update the monster"""
        self.rect.x += self.dx*self.velocity
        self.rect.y += self.dy*self.velocity

        # Bounce the monster off the edges of the display
        if self.rect.left <= self.screen_rect.left or self.rect.right >= self.screen_rect.right:
            self.dx = -1*self.dx
        if self.rect.top <= self.screen_rect.top or self.rect.bottom >= self.screen_rect.bottom:
            self.dy = -1*self.dy

    def set_position(self, position:tuple):
        self.rect.topleft = position
        

if __name__ == "__main__":
    pygame.init()
    ennemies = Ennemies(screen=pygame.display.set_mode((1200, 600))).ennemies_lst
    monster = Monster(settings=ennemies[0], screen=pygame.display.set_mode((1200, 600)), zone=pygame.Rect(0, 0, 1200, 600))
                      