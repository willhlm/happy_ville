import random

import pygame
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG 
from .states import AttackMain, AttackPre, Chase, Death, Patrol

TORPEDO_STATES = {
    'patrol': Patrol,
    'chase': Chase,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'death': Death,
}

class SmallBee(FlyingEnemy):#torpedo
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['mygga']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/small_bee/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.swarm_seed = random.uniform(0, 2 * 3.141592653589793)
        self.swarm_side_bias = random.choice([-1, 1])
        self.swarm_side_offset = random.randint(*self.config['behavior']['swarm_side_offset'])
        self.swarm_height_offset = random.randint(*self.config['behavior']['swarm_height_offset'])
        self.swarm_attack_commit = random.randint(*self.config['behavior']['attack_commit_time'])
        self.swarm_attack_jitter = [random.uniform(-0.2, 0.2), random.uniform(-0.12, 0.12)]
            
        self.health = self.config['health']  
        self.currentstate = StateManager(self, custom_states = TORPEDO_STATES, type = 'flying', universal_states = ['dead', 'death', 'hurt', 'attack_pre', 'attack_main', 'wait'])

    def knock_back(self, amp, dir):
        amp = [16,16]
        self.velocity[0] = dir[0]*amp[0]
        self.velocity[1] = -dir[1]*amp[1]
