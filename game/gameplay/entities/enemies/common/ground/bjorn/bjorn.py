import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox

from gameplay.entities.enemies.common.shared.states.state_manager import StateManager
from .config import ENEMY_CONFIG as BJORN_CONFIG

from .states import RollAttackPre, RollAttackMain, RollAttackPost, AttackPre, AttackMain, AttackPost, SlamPre, SlamMain, SlamPost
from .deciders import RollAttackDecider, SlamAttackDecider

from gameplay.entities.projectiles.utils.chain_spawner import ChainSpawner
from gameplay.entities.projectiles import SlamAttack

BJORN_STATES = {
    'roll_attack_pre': RollAttackPre,
    'roll_attack_main': RollAttackMain,
    'roll_attack_post': RollAttackPost,
    'attack_pre':AttackPre,
    'attack_main':AttackMain,
    'attack_post':AttackPost,
    'slam_pre':SlamPre,
    'slam_main':SlamMain,
    'slam_post':SlamPost,    
}

BJORN_DECIDERS = {
    'roll_attack': RollAttackDecider,
    'slam_attack': RollAttackDecider,
}

class Bjorn(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = BJORN_CONFIG['bjorn']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/bjorn/', game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)

        self.health = self.config['health']    
        self.currentstate = StateManager(self, type = 'ground', custom_states = BJORN_STATES, custom_deciders = BJORN_DECIDERS)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = self.dir, size = [64, 32])#make the object
        self.projectiles.add(attack)#add to group but in main phase         

    def slam(self):#called from states, attack main
        self.game_objects.signals.emit('fall_projectiles')
