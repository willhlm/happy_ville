import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from . import states_butterfly

class Butterfly(FlyingEnemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/boss/butterfly/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos,self.image.size)
        self.hitbox = self.rect.copy()
        self.currentstate = states_butterfly.Idle(self)
        self.health =20

    def knock_back(self,dir):
        pass

    def group_distance(self):
        pass

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('butterfly_killed')

    def right_collision(self,block, type = 'Wall'):
        pass

    def left_collision(self,block, type = 'Wall'):
        pass

    def down_collision(self,block):
        pass

    def top_collision(self,block):
        pass