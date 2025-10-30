import pygame, random
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from .larv_jr import LarvJr
from config.enemy import ENEMY_CONFIG 

class Larv(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['base']

        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/ground/larv/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)

        self.patrol_speed = self.config['speeds']['patrol']
        self.patrol_timer = 100

        self.attack_distance = [0,0]
        self.currentstate.enter_state('Patrol')

    def loots(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery - 10]
        number = random.randint(2, 4)
        for i in range(0, number):
            obj = LarvJr(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)