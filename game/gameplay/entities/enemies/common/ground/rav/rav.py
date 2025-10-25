import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.enemies.common.shared.states.state_manager import StateManager
from .config import ENEMY_CONFIG as RAV_CONFIG

from .states import JumpAttackPre, JumpAttackMain, JumpAttackPost, JumpBackPre, JumpBackMain, Hurt
from .deciders import JumpAttackDecider

RAV_STATES = {
    'jump_attack_pre': JumpAttackPre,
    'jump_attack_main': JumpAttackMain,
    'jump_attack_post': JumpAttackPost,
    'jump_back_pre': JumpBackPre,
    'jump_back_main': JumpBackMain,
    'hurt': Hurt,
}

RAV_DECIDERS = {
    'jump_attack': JumpAttackDecider,
}

class Rav(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.config = RAV_CONFIG['rav']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/rav/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)        

        self.health = self.config['health']    
        self.currentstate = StateManager(self, type = 'ground', custom_states = RAV_STATES, custom_deciders = RAV_DECIDERS)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = self.dir, size = [32, 32])#make the object
        self.projectiles.add(attack)#add to group but in main phase