import pygame, random
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import states_froggy

class Froggy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/froggy/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health = 1
        self.flags['aggro'] = False
        self.attack_distance = [150,50]

        self.currentstate = states_froggy.Idle(self)
        self.inventory = {'Amber_droplet':random.randint(5,15)}#thigs to drop wgen killed

    def knock_back(self,dir):
        pass