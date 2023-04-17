# Standard Python Modules
import os
import random
from typing import Any

# External Python Modules
import pygame
from pygame.math import Vector2 as vector   # to use 2D vectors

# Personal Python Modules
from const import *
from dashboard import Dashboard
from ennemies import Ennemies, Monster
from player import Player
from utils.parameterfile import ParameterFile
from utils.coloredlog import ColorLogger

# TODO
# - DONE: Warp only when not on safe zone
# - DONE: test monsters with other size
# - DONE: Restructure the yaml file in game
# - DONE: Check catch is OK using Name instead of colot
# - DONE: Add more try/except when loading all setting files
# - How to validate format of fields in YAMLL file --> use schema library
# - Add more logging for debugging purpose
# - Add a first page before starting (other then the pause one use currently)
# - DONE: Add a page when end of the round with time, bonus, etc
# - Add possibility to safe name & display TOP 10 scores
# - Load image or animated sprites using parameters
# - New element like bonus (coins, increase warp, increase live)
# - New element like damage (speed-up monsters, new monsters, reduce play zone, reduce monster size)
# - Add a game option with 
#       - limited time to carch all monsters
#       - extra bonus/malus


class Game():
    """A class to control gameplay"""
    def __init__(self, logger:ColorLogger=None):
        """Initilize the game object"""
        self.logger = logger

        # load game settings
        self.param_file = os.path.join(SETTINGS,"game.yaml")
        self.settings = ParameterFile(self.param_file, logger).parameters
        if not self.settings:
            exit()
        else :
            if self.logger:
                self.logger.info(f"Game settings: {self.settings}")

            self._init_var_from_settings()
            
            #Set game values
            self.exit = False
            self.is_paused = False
            self.dashboard_zone = pygame.Rect(0, 0, self.screen_size.x, self.dashboard_zone_height)  # TOP of screen
            self.safe_zone = pygame.Rect(0, self.screen_size.y-self.safe_zone_height+1, self.screen_size.x, self.safe_zone_height)  # Bottom of screen
            self.play_zone = pygame.Rect(0, self.dashboard_zone_height+1, self.screen_size.x, self.screen_size.y - self.dashboard_zone_height - self.safe_zone_height)   # Middle of Screen
            
            # Initialize Screen
            # pygame.mixer.pre_init(44100, -16, 2, 4096)    # Not sure about usage
            pygame.init()
            pygame.display.set_caption(self.title)
            if self.icon_path:
                self.icon = pygame.image.load(self.icon_path)
                pygame.display.set_icon(self.icon)

            self.screen = pygame.display.set_mode(self.screen_size)
            self.screen_rect = self.screen.get_rect()
            self.clock = pygame.time.Clock()

            #Set sounds and music
            self.next_level_sound = pygame.mixer.Sound(file=self.sound_path_next_level)

            #Set font
            self.font = pygame.font.Font(self.font_path, size=self.font_size)
            
            # Create all sprite groups
            self.player_group = pygame.sprite.Group()
            self.monster_group = pygame.sprite.Group()

            # Initialize Player
            self.player = Player(play_zone=self.play_zone, safe_zone=self.safe_zone, logger=self.logger)
            self.player_group.add(self.player)

            # Initialize Monsters
            self.ennemies_lst = Ennemies(logger=self.logger).ennemies_lst

            # Initialize the dashboard
            self.dashboard = Dashboard(screen=self.screen, zone=self.dashboard_zone, logger=self.logger)

    def _init_var_from_settings(self):
        try:
            self.title = self.settings["Title"]
            self.icon_path = self.settings["Icon"]
            self.FPS = self.settings["FPS"]

            self.screen_size = vector(self.settings["Screen"]["Size"])
            self.dashboard_zone_height = self.settings["Screen"]["DashboardHeight"]
            self.safe_zone_height = self.settings["Screen"]["SafeZoneHeight"]
            
            self.font_path:str = self.settings["Font"]["Path"]
            self.font_size:int = self.settings["Font"]["Size"]
            self.font_color:tuple = self.settings["Font"]["Color"]
            self.background_color:tuple = self.settings["Background"]["Color"]
            self.background_image_path:str = self.settings["Background"]["Image"]

            self.music_path_play:str = self.settings["Music"]["Play"]
            self.music_path_pause:str = self.settings["Music"]["Pause"]

            self.sound_path_next_level:str = self.settings["Sound"]["NextLevel"]
        except Exception as e:
            if self.logger:
                self.logger.error(f"{str(e)} field not found in {self.param_file} !")
                self.logger.error(f"EXIT PROGRAM !!!")
            else:
                print("ERROR:", f"{str(e)} field not found in {self.param_file} !")
                print("ERROR:", f"EXIT PROGRAM !!!")
            exit()

    def update(self):
        #Fill the display
        self.screen.fill(self.background_color)
        self.draw_safezone()
        
        #Update and draw sprite groups
        self.player_group.update()
        self.player_group.draw(self.screen)
        self.monster_group.update()
        self.monster_group.draw(self.screen)

        #Update and draw the Dashboard
        self.dashboard.update_timestamp(FPS=self.FPS)
        self.dashboard.draw(lives=self.player.lives, warps=self.player.warps, target_monster_image=self.target_monster_hud_image)

        # Color the play zone with the color of the target monster
        pygame.draw.rect(self.screen, self.target_monster.color, self.play_zone, 4)

        #Check for collisions
        self.check_collisions()

        #Update display and tick clock
        pygame.display.update()
        self.clock.tick(self.FPS)

    def check_collisions(self):
        """Check for collisions between player and monsters"""
        #Check for collision between a player and an indiviaual monster
        #WE must test the type of the monster to see if it matches the type of our target monster
        collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)

        #We collided with a monster
        if collided_monster:
            #Caught the correct monster
            if collided_monster.name == self.target_monster.name:
                self.dashboard.add_score()
                self.target_monster.sound.play()
                #Remove caught monster
                collided_monster.remove(self.monster_group)
                if (self.monster_group):
                    #There are more monsters to catch
                    self.choose_new_target()
                else:
                    #The round is complete
                    self.player.reset_position()
                    self.start_new_round()
            #Caught the wrong monster
            else:
                self.player.die_sound.play()
                self.player.lives -= 1
                self.player.reset_position()
                #Check for game over
                if self.player.lives <= 0:
                    self.game_over()

    def choose_new_target(self):
        """Choose a new target monster for the player"""
        self.target_monster = random.choice(self.monster_group.sprites())
        self.target_monster_hud_image = self.target_monster.image                           

    def draw_safezone(self):
        text_margin = 10
        safezone_text = self.font.render("Safe Zone (press space to come here)", True, self.font_color )
        safezone_rect = safezone_text.get_rect()
        safezone_rect.centerx = self.safe_zone.centerx
        safezone_rect.top = self.safe_zone.top + text_margin

        #Blit the safe zone
        pygame.draw.rect(self.screen, (171,219,227), self.safe_zone, 0)
        self.screen.blit(safezone_text, safezone_rect)

    def game_over(self):
        self.player.reset_position()
        self.pause_game(f"Game Over", enter_to_text="play again", reset_backround=False)
        self.reset_game()

    def input_player(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_paused = False
                self.quit_game()
            if event.type == pygame.KEYDOWN:
                # Action when game is running
                if not self.exit and not self.is_paused:
                    if event.key == pygame.K_SPACE:
                        self.player.warp()
                    elif event.key == pygame.K_p:
                        self.pause_game("PAUSED", enter_to_text="continue")
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        self.quit_game()
                    elif event.key == pygame.K_r:
                        self.reset_game()
                # Actions when game is paused
                elif self.is_paused:
                    if event.key == pygame.K_RETURN:
                        self.is_paused = False
                    elif event.key == pygame.K_q:
                        self.is_paused = False
                        self.quit_game()

    def main_game_loop(self):
        """The main game loop"""
        while not self.exit:
            #Update and draw the Game
            self.update()
            #Check to see if user wants to quit or pause
            self.input_player()

        #End the game
        pygame.quit()
    
    def pause_game(self, msg, enter_to_text, reset_backround=True):
        """Pause the game"""
        #Create the main pause text
        msg = self.font.render(msg, True, self.font_color )
        main_rect = msg.get_rect()
        main_rect.center = self.screen_rect.center

        #Create the 'Enter to' text
        sub_text = self.font.render(f"Press 'Enter' to {enter_to_text}", True, self.font_color )
        sub_rect = sub_text.get_rect()
        sub_rect.center = (main_rect.centerx, main_rect.centery + 64)

        #Display the pause text
        if reset_backround:
            self.screen.fill(self.background_color)
        self.screen.blit(msg, main_rect)
        self.screen.blit(sub_text, sub_rect)
        pygame.display.update()

        #Pause the game
        self.is_paused = True
        while self.is_paused:
            self.input_player()

    def quit_game(self):
        self.exit = True
        
    def reset_game(self):
        """Reset the game"""
        self.dashboard.reset_score()
        self.player.reset_lives()
        self.player.reset_position()
        self.start_new_round()
    
    def start_new_round(self):
        """Populate board with new monsters"""
        if self.dashboard.round_number > 0:
            #Provide a score bonus based on how quickly the round was finished
            self.dashboard.get_bonus()
            self.pause_game(f"level {self.dashboard.round_number} completed on {self.dashboard.round_time} sec. Bonus Points : {self.dashboard.bonus}", 
                            enter_to_text="for next level")

        #Reset round values
        self.dashboard.new_round()
        self.player.warps += 1

        #Remove any remaining monsters from a game reset
        for monster in self.monster_group:
            self.monster_group.remove(monster)

        #Add monsters to the monster group
        cnt = 0
        for i in range(self.dashboard.round_number):
            for ennemy in self.ennemies_lst:
                monster = Monster(settings=ennemy, play_zone=self.play_zone, logger=self.logger)
                self.monster_group.add(monster)

        #Choose a new target monster
        self.choose_new_target()
        self.next_level_sound.play()

    def test_reduce_playzone(self):
        """ Reduce the play zone & increse safe zone heights"""
        self.play_zone.height -= 10
        self.safe_zone.y -= 10
        self.safe_zone.height += 10

if __name__ == "__main__":
    game = Game()
    game.start_new_round()
    game.main_game_loop()