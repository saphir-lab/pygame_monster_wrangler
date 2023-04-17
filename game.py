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
from safezone import SafeZone
from utils.parameterfile import ParameterFile
from utils.coloredlog import ColorLogger

# TODO
# - DONE: Warp only when not on safe zone
# - DONE: test monsters with other size
# - DONE: Restructure the yaml file in game
# - DONE: Check catch is OK using Name instead of colot
# - DONE: Add more try/except when loading all setting files
# - DONE: Dediced class to draw safezone
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
            self.clock = pygame.time.Clock()

            # Initialize Screen
            # pygame.mixer.pre_init(44100, -16, 2, 4096)    # Not sure about usage
            pygame.init()
            pygame.display.set_caption(self.title)
            if self.icon_path:
                self.icon = pygame.image.load(self.icon_path)
                pygame.display.set_icon(self.icon)

            # Set screen Regions
            self.screen = pygame.display.set_mode(self.screen_size)
            self.screen_rect = self.screen.get_rect()
            self.dashboard = Dashboard(screen=self.screen, logger=self.logger) # TOP of screen
            self.safezone = SafeZone(screen=self.screen, logger=self.logger) # BOTTOM of screen
            self.playzone = pygame.Rect(0, self.dashboard.zone_height+1, self.screen_size.x, self.screen_size.y - self.dashboard.zone_height - self.safezone.zone_height)   # Middle of Screen

            #Set sounds and music
            self.next_level_sound = pygame.mixer.Sound(file=self.sound_path_next_level)

            #Set font
            self.font = pygame.font.Font(self.font_path, size=self.font_size)
            
            # Create all sprite groups
            self.player_group = pygame.sprite.Group()
            self.monster_group = pygame.sprite.Group()

            # Initialize Player
            self.player = Player(play_zone=self.playzone, safe_zone=self.safezone.screen_rect, logger=self.logger)
            self.player_group.add(self.player)

            # Initialize Monsters
            self.ennemies_lst = Ennemies(logger=self.logger).ennemies_lst

    def _init_var_from_settings(self):
        try:
            self.title = self.settings["Title"]
            self.icon_path = self.settings["Icon"]
            self.FPS = self.settings["FPS"]
            self.screen_size = vector(self.settings["ScreenSize"])
            
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

    def update(self, msg1:pygame.Surface=None, msg2:pygame.Surface=None):
        #Fill the display
        self.screen.fill(self.background_color)
        self.safezone.draw()
        
        # Update elements when not paused
        if not self.is_paused:
            self.dashboard.update_timestamp(FPS=self.FPS)
            self.player_group.update()
            self.monster_group.update()
            self.check_collisions()

        # draw sprite groups
        self.player_group.draw(self.screen)
        self.monster_group.draw(self.screen)

        #draw Dashboard & Color the play zone with the color of the target monster
        self.dashboard.draw(lives=self.player.lives, warps=self.player.warps, target_monster_image=self.target_monster_hud_image)
        pygame.draw.rect(self.screen, self.target_monster.color, self.playzone, 4)

        # Display pause text
        if msg1:
            msg1_rect = msg1.get_rect()
            msg1_rect.center = self.screen_rect.center
            self.screen.blit(msg1, msg1_rect)
        if msg2:
            msg2_rect = msg2.get_rect()
            msg2_rect.center = (self.screen_rect.centerx, self.screen_rect.centery + (self.font_size * 2))
            self.screen.blit(msg2, msg2_rect)

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

    def game_over(self):
        self.player.reset_position()
        self.pause_game(f"Game Over", enter_to_text="play again", with_animation=True)
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
    
    def pause_game(self, msg, enter_to_text, with_animation=False):
        """Pause the game"""
        #Create the pause text
        msg = self.font.render(msg, True, self.font_color)
        sub_text = self.font.render(f"Press 'Enter' to {enter_to_text}", True, self.font_color )

        #Pause the game
        self.is_paused = True
        while self.is_paused:
            if with_animation:             
                #Update and draw sprite groups
                self.monster_group.update()
            self.update(msg1=msg, msg2=sub_text)
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
                monster = Monster(settings=ennemy, play_zone=self.playzone, logger=self.logger)
                self.monster_group.add(monster)

        #Choose a new target monster
        self.choose_new_target()
        self.next_level_sound.play()

    def test_reduce_playzone(self):
        """ Reduce the play zone & increse safe zone heights"""
        self.playzone.height -= 10
        self.safezone.screen_rect.y -= 10
        self.safezone.screen_rect.height += 10

if __name__ == "__main__":
    game = Game()
    game.start_new_round()
    game.main_game_loop()