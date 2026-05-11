import pygame
from engine.utils.functions import sign
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG

from .states import AttackPre, AttackMain, AttackPost

SPORTPUFF_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost
}

class SporePuff(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['spore_puff']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/spore_puff/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)        

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type='ground', custom_states = SPORTPUFF_STATES)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = [0,0], size = [32, 32])#make the object
        self.game_objects.projectiles.add_enemy(attack)#add to group but in main phase
