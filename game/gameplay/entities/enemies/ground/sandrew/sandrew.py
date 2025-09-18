import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import states_sandrew
from gameplay.entities.projectiles import HurtBox

class Sandrew(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/sandrew/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [200, 25]
        self.aggro_distance = [250, 25]#at which distance to the player when you should be aggro. Negative value make it no going aggro
        self.attack = HurtBox