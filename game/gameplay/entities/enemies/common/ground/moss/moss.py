import pygame
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.projectiles import HurtBox

from .config import ENEMY_CONFIG as MOSS_CONFIG
from .states import AttackPre, AttackMain, AttackPost

MOSS_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost
}

class Moss(Enemy):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.config = MOSS_CONFIG["moss"]
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/enemies/common/ground/moss/", game_objects)

        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.currentstate = StateManager(self, type = 'ground', custom_states = MOSS_STATES)

        self.vitals.set_max_health(self.config["health"])
        self.vitals.set_health(self.vitals.max_health)

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 20, dir = [0, 0], size = [64, 64])#make the object
        self.game_objects.projectiles.add_enemy(attack)#add to group but in main phase
