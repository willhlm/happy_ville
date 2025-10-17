import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from .config import ENEMY_CONFIG 
from gameplay.entities.projectiles import HurtBox

from gameplay.entities.shared.states.enemy.state_manager import StateManager

from .states import HidePre, HideMain, HidePost
from .deciders import CheckSafeDecider

TAGGMUS_STATES = {
    'hide_pre': HidePre,
    'hide_main': HideMain,
    'hide_post': HidePost,
}

TAGGMUS_DECIDERS = {
    'check_safe': CheckSafeDecider,
}

class TaggMus(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['base']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/tagg_mus/', game_objects, flip_x = True)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/ground/tagg_mus/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)

        self.health = self.config['health']   
        self.currentstate = StateManager(self, custom_states = TAGGMUS_STATES, custom_deciders = TAGGMUS_DECIDERS)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = [0,0], size = [64, 64])#make the object
        self.projectiles.add(attack)#add to group but in main phase