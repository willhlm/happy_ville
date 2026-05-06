import random

import pygame
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG
from .states import AttackMain, AttackPost, AttackPre, Chase, Death, Hurt, Patrol

RAVEN_STATES = {
    'patrol': Patrol,
    'chase': Chase,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
    'hurt': Hurt,
    'death': Death,
}

class Raven(FlyingEnemy):#Raven,  
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['raven']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/raven/',game_objects, flip_x = True)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/raven/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
            
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(
            self,
            custom_states = RAVEN_STATES,
            type = 'flying',
            universal_states = ['dead', 'death', 'hurt', 'wait']
        )

        self.shader_state.add_shader('aura', colour = [0,0,0], size = 0.3, fall_off = 4, noise_intensity = 3)
        self.time = 0
        
    def update_render(self, dt):
        super().update_render(dt)
        self.release_particles(dt)
 
    def release_particles(self, dt):
        self.time += dt 
        if self.time > 40:
            rect = self.hitbox
            position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(rect[3]*0.1,rect[3]*0.5)]
            self.game_objects.particles.emit("spirit_wisp", pos=position, n=1, colour=(0,0,0,255))            
            self.time = 0
