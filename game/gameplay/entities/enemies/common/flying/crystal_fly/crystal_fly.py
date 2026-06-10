import pygame
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from engine.utils import read_files
from gameplay.entities.projectiles import CrystalTagg
from .config import ENEMY_CONFIG

class CrystalFly(FlyingEnemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['crystal_fly']
        self.sprites = read_files.load_sprites_dict(
            'assets/sprites/entities/enemies/common/flying/crystal_fly/',
            game_objects,
        )
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(
            self,
            type='flying',
            universal_states=['dead', 'death', 'hurt', 'attack_pre', 'attack_main', 'wait'],
        )

    def attack(self):
        dirs = [[1,1], [-1,1], [1,-1], [-1,-1]]
        for direction in dirs:
            obj = CrystalTagg(self.hitbox.center, self.game_objects, dir=direction, amp=[3, 3])
            self.game_objects.projectiles.add_enemy(obj)
