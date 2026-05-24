import pygame
import copy
import random
from engine.utils.functions import sign
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from .config import ENEMY_CONFIG

from .states import AttackPre, AttackMain, AttackPost, Seed, Grow, Plant, Spawn

SPORTPUFF_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
    'seed': Seed,
    'grow': Grow,
    'plant': Plant,
    'spawn': Spawn,
}

class SporePuff(Enemy):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos,game_objects)
        self.config = copy.deepcopy(ENEMY_CONFIG['spore_puff'])
        if 'initial_state' in kwargs:
            self.config['initial_state'] = kwargs['initial_state']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/spore_puff/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 32, 32)
        self.true_pos = list(self.rect.topleft)

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type='ground', custom_states = SPORTPUFF_STATES)
        self.velocity = list(kwargs.get("seed_velocity", [0, 0]))

    def attack(self):#called from states, attack main
        attack = HurtBox(self, lifetime = 10, dir = [0,0], size = [32, 32])#make the object
        self.game_objects.projectiles.add_enemy(attack)#add to group but in main phase
        self.spawn_seed_puffs()

    def spawn_seed_puffs(self):
        seed_cfg = self.config["seed"]
        count = random.randint(seed_cfg["count"][0], seed_cfg["count"][1])
        horizontal_min, horizontal_max = seed_cfg["horizontal_speed"]
        vertical_min, vertical_max = seed_cfg["vertical_speed"]
        base_midbottom = self.hitbox.midbottom

        for _ in range(count):
            horizontal_speed = random.uniform(horizontal_min, horizontal_max)
            vertical_speed = random.uniform(vertical_min, vertical_max)
            launch_dir = random.choice([-1, 1])

            child = SporePuff(
                [base_midbottom[0], base_midbottom[1]],
                self.game_objects,
                initial_state="seed",
                seed_velocity=[horizontal_speed * launch_dir, vertical_speed],
            )
            child.rect.midbottom = base_midbottom
            child.hitbox.midbottom = base_midbottom
            child.true_pos = list(child.rect.topleft)
            child.dir[0] = sign(child.velocity[0]) if child.velocity[0] != 0 else self.dir[0]
            self.game_objects.enemies.add(child)
