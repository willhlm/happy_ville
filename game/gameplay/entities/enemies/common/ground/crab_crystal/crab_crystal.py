import pygame 
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.surface_crawler import Fall, Hurt, Land, Patrol, SurfaceCrawlerEnemy, Wait
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG

CRAB_CRYSTAL_STATES = {
    'patrol': Patrol,
    'fall': Fall,
    'land': Land,
    'wait': Wait,
    'hurt': Hurt,
}

class CrabCrystal(SurfaceCrawlerEnemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.config = ENEMY_CONFIG['crab_crystal']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/crab_crystal/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        movement_config = self.config['movement']

        self.init_surface_stick_motion(probe_distance = movement_config['probe_distance'], corner_inset = movement_config['corner_inset'])
        self.currentstate = StateManager(self, type = 'ground', custom_states = CRAB_CRYSTAL_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])

    def take_dmg(self, effect):
        effect.defender_callbacks.pop('particles', None)
        effect.attacker_callbacks.pop('sword_jump', None)
        effect.defender_callbacks['hitstop'] = lambda eff: eff.defender.hitstop.start(duration = eff.hitstop, callback = [])#removes the knock back but keep the hitstop
        return effect
