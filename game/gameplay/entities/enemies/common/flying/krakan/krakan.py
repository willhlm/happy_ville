import pygame
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG 
from .states import AirPatrol, AttackMain, AttackPost, AttackPre, Chase, Death, GroundWalk, Hurt, Patrol

KRAKAN_STATES = {
    'patrol': Patrol,
    'ground_walk': GroundWalk,
    'air_patrol': AirPatrol,
    'chase': Chase,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
    'hurt': Hurt,
    'death': Death,
}

class Krakan(FlyingEnemy):#Raven,  
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['krakan']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/krakan/',game_objects, flip_x = True)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/krakan/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
            
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(
            self,
            custom_states = KRAKAN_STATES,
            type = 'flying',
            universal_states = ['dead', 'death', 'hurt', 'attack_pre', 'attack_main', 'attack_post', 'wait']
        )
