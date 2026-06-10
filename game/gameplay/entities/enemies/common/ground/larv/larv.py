import pygame, random

from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.enemies.common.shared.surface_crawler import Fall, Hurt, Land, Patrol, SurfaceCrawlerEnemy, Wait

from .larv_jr import LarvJr
from .config import ENEMY_CONFIG
from .hanging_component import HangingComponent
from .states import Hanging

LARV_STATES = {
    'patrol': Patrol,
    'fall': Fall,
    'hanging': Hanging,
    'land': Land,
    'wait': Wait,
    'hurt': Hurt,
}

class Larv(SurfaceCrawlerEnemy):
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

        if initial_state == 'hanging' or anchor_pos is not None:
            self.hanging_component = HangingComponent(self, initial_state = initial_state, anchor_pos = anchor_pos)
            self.hanging_component.init_motion()
        self.init_surface_stick_motion(
            probe_distance = movement_config['probe_distance'],
            corner_inset = movement_config['corner_inset'],
            enabled = initial_state != 'hanging',
        )

        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])
        self.hanging_component.enter_initial_state()

    def _emit_loot(self):#spawn minions
        pos = [self.hitbox.centerx,self.hitbox.centery - 10]
        number = random.randint(2, 4)
        for i in range(0, number):
            obj = LarvJr(pos,self.game_objects)
            obj.velocity = [random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)
