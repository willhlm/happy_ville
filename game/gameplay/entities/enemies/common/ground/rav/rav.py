import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import rav_states
from gameplay.entities.projectiles import HurtBox
from .state_manager import RavStateManager
from config.enemies import ENEMY_CONFIGS

class Rav(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIGS['rav']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/rav/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)        

        self.health = self.config['health']
        self.chase_speed = self.config['speeds']['chase']
        self.patrol_speed = self.config['speeds']['patrol']
        self.patrol_timer = self.config['timers']['patrol']
        
        self.aggro_distance = self.config['distances']['aggro']
        self.attack_distance = self.config['distances']['attack']
        self.jump_distance = self.config['distances']['jump']
        self.flags['jump_attack_able'] = True

        self.currentstate = RavStateManager(self)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = self.dir, size = [32, 32])#make the object
        self.projectiles.add(attack)#add to group but in main phase