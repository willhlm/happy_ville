import random

import pygame

from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager

from .config import ENEMY_CONFIG
from .states import Crawl, Wait
from .surface_larv import SurfaceLarv

LARV_JR_STATES = {
    'crawl': Crawl,
    'wait': Wait,
}

class LarvJr(SurfaceLarv):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['larv_jr']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv_jr/', game_objects, True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 22, 12)
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.surface_patrol_time = 0
        movement_config = self.config['movement']

        self.init_surface_stick_motion(
            speed = movement_config.get('crawl_speed', self.config['speeds']['crawl']),
            stick_speed = movement_config['stick_speed'],
            probe_distance = movement_config['probe_distance'],
            corner_inset = movement_config['corner_inset'],
        )
        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_JR_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])

    def update_surface_crawl_state(self, dt, player_distance):
        if self.surface_patrol_time <= 0:
            patrol_cfg = self.config['patrol']
            self.surface_patrol_time = random.randint(patrol_cfg['crawl_time'][0], patrol_cfg['crawl_time'][1])

        self.surface_patrol_time -= dt
        if self.surface_patrol_time > 0:
            return

        wait_cfg = self.config['patrol']['wait_time']
        self.currentstate.enter_state('wait', time = random.randint(wait_cfg[0], wait_cfg[1]), next_state = 'crawl', turn = True)
        self.surface_patrol_time = 0

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('larv_jr_killed')#emit this signal
