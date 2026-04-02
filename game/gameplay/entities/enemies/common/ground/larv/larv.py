import random

import pygame

from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager

from .larv_jr import LarvJr
from .config import ENEMY_CONFIG
from .hangable_larv import HangableLarv
from .states import Dropping, Hanging, Land

LARV_STATES = {
    'hanging': Hanging,
    'dropping': Dropping,
    'land': Land,
}

class Larv(HangableLarv):
    def __init__(self, pos, game_objects, initial_state = None, anchor_pos = None):
        super().__init__(pos, game_objects, initial_state = initial_state, anchor_pos = anchor_pos)
        self.config = ENEMY_CONFIG['larv']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/ground/larv/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.health = self.config['health']

        self.init_hanging_motion()

        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])
        self.enter_initial_hanging_state()

    def _emit_loot(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery - 10]
        number = random.randint(2, 4)
        for i in range(0, number):
            obj = LarvJr(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)
