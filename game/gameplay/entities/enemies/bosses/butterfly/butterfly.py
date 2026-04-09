import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from . import states_butterfly

class Butterfly(FlyingEnemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/bosses/butterfly/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos,self.image.size)
        self.hitbox = self.rect.copy()
        self.currentstate = states_butterfly.Idle(self)
        self.vitals.set_max_health(20)
        self.vitals.set_health(self.vitals.max_health)

    def knock_back(self,dir):
        pass

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('butterfly_killed')
