import random

import pygame

from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager

from .larv_jr import LarvJr
from .config import ENEMY_CONFIG
from .hanging_component import HangingComponent
from .surface_larv import SurfaceLarv
from .states import Crawl, Dropping, Hanging, Land, Wait

LARV_STATES = {
    'crawl': Crawl,
    'hanging': Hanging,
    'dropping': Dropping,
    'land': Land,
    'wait': Wait,
}

class Larv(SurfaceLarv):
    def __init__(self, pos, game_objects, initial_state = None, anchor_pos = None):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['larv']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/ground/larv/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        movement_config = self.config['movement']
        self.surface_patrol_time = 0
        if initial_state == 'hanging' or anchor_pos is not None:
            self.attach_hanging_component(HangingComponent(self, initial_state = initial_state, anchor_pos = anchor_pos))
            self.hanging_component.init_motion()
        self.init_surface_stick_motion(
            speed = movement_config.get('crawl_speed', self.config['speeds']['crawl']),
            stick_speed = movement_config['stick_speed'],
            probe_distance = movement_config['probe_distance'],
            corner_inset = movement_config['corner_inset'],
            enabled = initial_state != 'hanging',
        )

        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])
        self.enter_initial_hanging_state()

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

    def _emit_loot(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery - 10]
        number = random.randint(2, 4)
        for i in range(0, number):
            obj = LarvJr(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)
