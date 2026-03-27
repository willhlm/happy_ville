import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.states.state_manager import StateManager
from .config import ENEMY_CONFIG
from .states import AttackPre, Charging, AttackMain, AttackPost

WILD_SWINE_STATES = {
    'attack_pre': AttackPre,
    'charging': Charging,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
}

class WildSwine(Enemy):
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['base']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/vildswine/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.health = self.config['health']
        self.currentstate = StateManager(self, custom_states=WILD_SWINE_STATES)
