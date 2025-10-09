import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.shared.states.enemy.state_manager import StateManager
from .config import ENEMY_CONFIG as HEDGE_CONFIG

from .states import Sleep, WakeUp

HEDGE_STATES = {
    'sleep': Sleep,
    'wake_up': WakeUp,
}

class Hedge(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.config = HEDGE_CONFIG['hedge']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/hedge/',game_objects, flip_x = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)        

        self.health = self.config['health']
        self.chase_speed = self.config['speeds']['chase']       
        self.aggro_distance = self.config['distances']['aggro']

        self.currentstate = StateManager(self, custom_states = HEDGE_STATES, custom_deciders = None)