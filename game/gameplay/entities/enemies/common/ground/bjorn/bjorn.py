import pygame, random
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from config.enemy import ENEMY_CONFIG 

class Bjorn(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['base']

        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/bjorn/', game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)

        self.patrol_speed = self.config['speeds']['patrol']
        self.patrol_timer = 100

        self.attack_distance = [0,0]
        self.currentstate.enter_state('Patrol')