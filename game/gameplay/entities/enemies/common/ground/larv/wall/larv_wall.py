import pygame

from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager

from ..surface_larv import SurfaceLarv
from ..states import Crawl
from .config import ENEMY_CONFIG

LARV_WALL_STATES = {
    'crawl': Crawl,
}

class LarvWall(SurfaceLarv):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['larv_wall']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/slime_wall/', game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.angle = 0
        self.friction = self.config['friction'].copy()
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.clockwise = -1 if kwargs.get('clockwise', True) in (False, 0, 'false', 'False', 'counterclockwise') else 1
        movement_config = self.config['movement']
        initial_side = kwargs.get('initial_side', 'bottom')
        self.init_surface_stick_motion(
            speed = movement_config['crawl_speed'] if 'crawl_speed' in movement_config else self.config['speeds']['crawl'],
            stick_speed = movement_config['stick_speed'],
            probe_distance = movement_config['probe_distance'],
            corner_inset = movement_config['corner_inset'],
            clockwise = self.clockwise > 0,
            initial_side = initial_side,
        )
        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_WALL_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])
