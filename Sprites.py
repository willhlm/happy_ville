import pygame
from os import listdir
from os.path import isfile, join

class Sprites():
    def __init__(self):
        # Add lists for each sprite animation here, in sub classes

        pass

    def load_sprites(self,path_to_folder):
        #use this to load multiple sprites in a path_to_folder

        list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
        if join(path_to_folder,'.DS_Store') in list_of_sprites:
            list_of_sprites.remove(join(path_to_folder,'.DS_Store'))
        return [pygame.image.load(file) for file in list_of_sprites]

    def load_single_sprite(self,path_to_sprite):
        #use to load single sprite, full path must be provided

        return pygame.image.load(path_to_sprite)

#class containing sprites for player
class Sprites_player(Sprites):

    player_path = "Sprites/player/"
    def __init__(self):
        super().__init__()
        self.run_right = self.load_sprites(self.player_path + "run/")
        self.run_left = [pygame.transform.flip(f, True, False) for f in self.load_sprites(self.player_path + "run/")]
        self.jump_right = self.load_sprites(self.player_path + "jump/")
        self.jump_left = [pygame.transform.flip(f, True, False) for f in self.load_sprites(self.player_path + "jump/")]
        self.hurt = self.load_sprites(self.player_path + "hurt/")
        self.death = self.load_sprites(self.player_path + "death/")
        self.attack_right = self.load_sprites(self.player_path + "attack_side/")
        self.attack_left = [pygame.transform.flip(f, True, False) for f in self.load_sprites(self.player_path + "attack_side/")]
        self.attack_up_right = self.load_sprites(self.player_path + "attack_up/")
        self.attack_up_left = [pygame.transform.flip(f, True, False) for f in self.load_sprites(self.player_path + "attack_up/")]
        self.attack_down_right = self.load_sprites(self.player_path + "attack_down/")
        self.attack_down_left = [pygame.transform.flip(f, True, False) for f in self.load_sprites(self.player_path + "attack_down/")]

class Sprites_evil_knight(Sprites):
