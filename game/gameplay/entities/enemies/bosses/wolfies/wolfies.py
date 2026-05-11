import pygame 
from gameplay.entities.enemies.base.boss import Boss
from gameplay.entities.shared.boss_rewards import ProgressionUnlockReward
from engine.utils import read_files
from gameplay.entities.enemies.bosses.shared import task_manager
from gameplay.entities.projectiles import HurtBox
from . import wolfies_states
from gameplay.entities.projectiles.utils.chain_spawner import ChainSpawner
from gameplay.entities.projectiles import SlamAttack
from .config import WOLFIES_CONFIG

class Wolfies(Boss):
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects, ID)        
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/bosses/wolfies/',game_objects, flip_x = True)
        self.image = self.sprites['idle_nice'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 35, 45)

        self.currentstate = task_manager.TaskManager(self, wolfies_states.STATE_REGISTRY, WOLFIES_CONFIG['patterns'])

        self.reward = ProgressionUnlockReward(
            preview_sprite='dash_ground_main',
            progress_key='dash',
        )
        self.attack_distance = WOLFIES_CONFIG['attack_distance']
        self.jump_distance = WOLFIES_CONFIG['jump_distance']
        self.vitals.set_max_health(WOLFIES_CONFIG['health'])
        self.vitals.set_health(self.vitals.max_health)

        self.light = self.game_objects.lights.create(self, radius=150)

    def kill(self):
        super().kill()
        self.game_objects.lights.remove(self.light)

    def attack(self, lifetime = 10):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = self.dir, size = [64, 64])#make the object
        self.game_objects.projectiles.add_enemy(attack)#add to group but in main phase

    def slam_attack(self):#called from states, attack main
        self.game_objects.cosmetics.add(ChainSpawner(self.rect.center, self.game_objects, SlamAttack, direction = self.dir, distance = 50, number = 5, frequency = 20))
