import pygame 
from engine.utils import read_files
from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from . import states_bird

#animals
class Bird(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/animals/bluebird/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_bird.Idle(self)
        self.flags['aggro'] = False
        self.health = 1
        self.aggro_distance = [100,50]#at which distance is should fly away

    def knock_back(self, amp, dir):
        pass