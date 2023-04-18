# Standard Python Modules
import os
from typing import Any

# External Python Modules
import pygame

# Personal Python Modules
from const import *
from utils.parameterfile import ParameterFile
from utils.coloredlog import ColorLogger


class Player(pygame.sprite.Sprite):
    """A player class that the user can control"""

    def __init__(self, play_zone: pygame.Rect, safe_zone: pygame.Rect, logger: ColorLogger = None):
        """Initialize the player"""
        super().__init__()
        self.logger = logger
        self.play_zone = play_zone
        self.safe_zone = safe_zone

        # load Player settings
        self.param_file = os.path.join(SETTINGS, "player.yaml")
        self.settings = ParameterFile(self.param_file, logger).parameters
        if self.logger:
            self.logger.info(f"Player settings: {self.settings}")
        self._init_var_from_settings()

        # Initialize sound & image
        self.die_sound = pygame.mixer.Sound(file=self.sound_path_die)
        self.warp_sound = pygame.mixer.Sound(file=self.sound_path_warp)
        self.image = pygame.transform.scale(
            pygame.image.load(self.image_path), self.size)
        self.rect = self.image.get_rect()
        self.reset_position()
        self.reset_lives()

    def _init_var_from_settings(self):
        """ Initialize instance variables from setting file content """
        try:
            self.starting_lives: int = self.settings["Lives"]
            self.starting_warps: int = self.settings["Warps"]
            self.velocity: int = self.settings["Velocity"]
            self.sprite: bool = self.settings["Sprite"]
            self.pause_when_die: bool = self.settings["PauseWhenDie"]
            self.image_path: str = self.settings["Image"]["Path"]
            self.size: tuple = self.settings["Image"]["Size"]
            self.sound_path_die: str = self.settings["Sound"]["die"]
            self.sound_path_warp: str = self.settings["Sound"]["warp"]
        except Exception as e:
            if self.logger:
                self.logger.error(
                    f"{str(e)} field not found in {self.param_file} !")
                self.logger.error(f"EXIT PROGRAM !!!")
            else:
                print(
                    "ERROR:", f"{str(e)} field not found in {self.param_file} !")
                print("ERROR:", f"EXIT PROGRAM !!!")
            exit()

    def update(self):
        """Update the player"""
        keys = pygame.key.get_pressed()

        # Move the player within the bounds of the screen
        if keys[pygame.K_LEFT] and self.rect.left >= self.play_zone.left + self.velocity:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right <= self.play_zone.width - self.velocity:
            self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top >= self.play_zone.top + self.velocity:
            self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom <= self.play_zone.bottom - self.velocity:
            self.rect.y += self.velocity

    def reset_lives(self):
        """Resets the players lives"""
        self.lives = self.starting_lives
        self.warps = self.starting_warps

    def reset_position(self):
        """Resets the players position"""
        self.rect.centerx = self.safe_zone.centerx
        self.rect.bottom = self.safe_zone.bottom

    def warp(self):
        """Warp the player to the bottom 'safe zone'"""
        # second condition to verify the player is not already in the safe zone
        if self.warps > 0 and self.rect.top < self.safe_zone.top:
            self.warps -= 1
            self.warp_sound.play()
            self.rect.bottom = self.safe_zone.bottom


if __name__ == "__main__":
    pygame.init()
    player = Player(pygame.display.set_mode((1200, 600)))
