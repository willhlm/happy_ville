import pygame

from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.enemies.common.shared.surface_crawler import Fall, Hurt, Land, Patrol, SurfaceCrawlerEnemy, Wait

from .config import ENEMY_CONFIG

LARV_JR_STATES = {
    'patrol': Patrol,
    'fall': Fall,
    'land': Land,
    'wait': Wait,
    'hurt': Hurt,
}

class LarvJr(SurfaceCrawlerEnemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['larv_jr']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv_jr/', game_objects, True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 22, 12)
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.inventory = {'amber_droplet':1}
        movement_config = self.config['movement']

        self.init_surface_stick_motion(
            probe_distance = movement_config['probe_distance'],
            corner_inset = movement_config['corner_inset'],
        )
        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_JR_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])

    def dead(self):#called when death animation is finished
        super().dead()
        self.game_objects.signals.emit('larv_jr_killed')#emit this signal
