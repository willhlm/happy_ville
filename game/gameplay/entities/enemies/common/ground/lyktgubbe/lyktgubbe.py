import pygame
from engine import constants as C

from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG as LYKTGUBBE_CONFIG

from .states import AttackPre, AttackMain, AttackPost

LYKTGUBBE_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost
}

class Lyktgubbe(Enemy):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos,game_objects)
        self.config = LYKTGUBBE_CONFIG['lyktgubbe']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/lyktgubbe/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)        
        self.controller_id = kwargs.get('id')

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type = 'ground', custom_states = LYKTGUBBE_STATES)

        self.light = self.game_objects.lights.add_light(self, colour = normlaised, radius = 100)
        self.shader_state.add_shader('aura', colour = C.spirit_colour[:3], size=0.3, fall_off=4, noise_intensity=3)

    def control(self):#called from attack
        if self.controller_id is None: return        
        self.game_objects.signals.emit('irrbloss_transform', source=self, controller_id = self.controller_id)

    def release_control(self):#called from attack end
        if self.controller_id is None: return        
        self.game_objects.signals.emit('release_irrbloss', source=self, controller_id = self.controller_id)
