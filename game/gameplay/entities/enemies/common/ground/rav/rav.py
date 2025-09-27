import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import rav_states
from gameplay.entities.projectiles import HurtBox

class Rav(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/rav/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)
        self.aggro_distance = [200, 20]#at which distance to the player when you should be aggro -> negative means no
        self.attack_distance = [50, 150]
        self.health = 3
        self.chase_speed = 0.8
        self.patrol_speed = 0.3
        self.patrol_timer = 220
        #self.animation.framerate = 0.2
        self.currentstate = rav_states.Patrol(self)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = self.dir, size = [32, 32])#make the object
        self.projectiles.add(attack)#add to group but in main phase