# Standard Python Modules
import os
from typing import Any

# External Python Modules
import pygame

# Personal Python Modules
from const import *
from ennemies import Monster
from utils.parameterfile import ParameterFile
from utils.coloredlog import ColorLogger


class Dashboard():
    def __init__(self, screen: pygame.Surface, logger: ColorLogger = None):
        self.logger = logger
        self.screen = screen

        # load Dashboard settings
        self.param_file = os.path.join(SETTINGS, "dashboard.yaml")
        self.settings = ParameterFile(self.param_file, logger).parameters
        if self.logger:
            self.logger.info(f"Dashboard settings: {self.settings}")
        self._init_var_from_settings()

        # Determine Rectangle for Dashboard at TOP of screen
        self.screen_rect = pygame.Rect(
            0, 0, screen.get_width(), self.zone_height)

        # Set background images
        if self.background_image_path:
            self.background_image = pygame.transform.scale(
                pygame.image.load(self.background_image_path), self.screen_rect.size)

        # Set font
        self.font = pygame.font.Font(self.font_path, size=self.font_size)

        # Dashboard elements
        self.reset_score()
        self.target_monster: Monster = None

    def _init_var_from_settings(self):
        """ Initialize instance variables from setting file content """
        try:
            self.zone_height: str = self.settings["Height"]
            self.font_path: str = self.settings["Font"]["Path"]
            self.font_size: int = self.settings["Font"]["Size"]
            self.font_color: tuple = self.settings["Font"]["Color"]
            self.background_color: tuple = self.settings["Background"]["Color"]
            self.background_image_path: str = self.settings["Background"]["Image"]
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

    def add_score(self):
        self.score += 100*self.round_number

    def draw(self, lives: int, warps: int, target_monster: Monster):
        """Draw the HUD and other to the display"""
        self.target_monster = target_monster
        text_margin = 10

        # Set text
        catch_text = self.font.render("Current Catch", True, self.font_color)
        catch_rect = catch_text.get_rect()
        catch_rect.centerx = self.screen_rect.centerx
        catch_rect.top = 5

        score_text = self.font.render(
            "Score: " + str(self.score), True, self.font_color)
        score_rect = score_text.get_rect()
        score_rect.topleft = (self.screen_rect.left + text_margin, 5)

        lives_text = self.font.render(
            "Lives: " + str(lives), True, self.font_color)
        lives_rect = lives_text.get_rect()
        lives_rect.topleft = (self.screen_rect.left + text_margin, 35)

        round_text = self.font.render(
            "Current Round: " + str(self.round_number), True, self.font_color)
        round_rect = round_text.get_rect()
        round_rect.topleft = (self.screen_rect.left + text_margin, 65)

        time_text = self.font.render(
            "Round Time: " + str(self.round_time), True, self.font_color)
        time_rect = time_text.get_rect()
        time_rect.topright = (self.screen_rect.right - text_margin, 5)

        warp_text = self.font.render(
            "Warps: " + str(warps), True, self.font_color)
        warp_rect = warp_text.get_rect()
        warp_rect.topright = (self.screen_rect.right - text_margin, 35)

        # Blit the Dashboard
        if self.background_color:
            pygame.draw.rect(self.screen, self.background_color,
                             self.screen_rect, 0)
        if self.background_image_path:
            self.screen.blit(self.background_image, self.screen_rect)
        self.screen.blit(catch_text, catch_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(round_text, round_rect)
        self.screen.blit(lives_text, lives_rect)
        self.screen.blit(time_text, time_rect)
        self.screen.blit(warp_text, warp_rect)

        # Blit the target monster & draw rectangle in associated color
        if self.target_monster:
            target_monster_rect = self.target_monster.image.get_rect()
            target_monster_rect.centerx = self.screen_rect.centerx
            target_monster_rect.bottom = self.screen_rect.bottom - 3
            self.screen.blit(self.target_monster.image, target_monster_rect)
        # pygame.draw.rect(self.screen, self.target_monster.color, target_monster_rect, 2)

    def get_bonus(self):
        # Provide a score bonus based on how quickly the round was finished
        self.bonus = int(10000*self.round_number/(1 + self.round_time))

    def new_round(self):
        self.get_bonus()
        self.score += self.bonus
        self.round_number += 1
        self.round_time = 0
        self.frame_count = 0

    def reset_score(self):
        self.score = 0
        self.bonus = 0
        self.round_number = 0
        self.round_time = 0
        self.frame_count = 0

    def update_timestamp(self, FPS):
        """Update timestamp following FPS"""
        self.frame_count += 1
        if self.frame_count == FPS:
            self.round_time += 1
            self.frame_count = 0


if __name__ == "__main__":
    pygame.init()
    dashboard = Dashboard(screen=pygame.display.set_mode((1200, 600)))
