import pygame
import math
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from .config import ENEMY_CONFIG 
from gameplay.entities.projectiles import Tagg

from gameplay.entities.enemies.common.shared.states.state_manager import StateManager

from .states import AttackPre, AttackMain, AttackPost, Retreat, Hurt
from .deciders import CheckSafeDecider, CheckPlayerAttackReadyDecider

TAGGMUS_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
    'retreat': Retreat,
    'hurt': Hurt,
}

TAGGMUS_DECIDERS = {
    'check_safe': CheckSafeDecider,
    'check_player_attack_ready': CheckPlayerAttackReadyDecider,
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
        self.tagg_burst_index = 0

    def emit_tagg_burst(self, angle_offset = 0, count = None, speed = None):
        attack_cfg = self.config['attacks']['tagg_burst']
        count = count or attack_cfg['counts'][0]
        speed = speed or attack_cfg['speed'][0]
        lifetime = attack_cfg['lifetime']
        spawn_radius = attack_cfg['spawn_radius']

        for index in range(count):
            angle = angle_offset + (math.tau * index / count)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            spawn_pos = (
                self.hitbox.centerx + math.cos(angle) * spawn_radius,
                self.hitbox.centery + math.sin(angle) * spawn_radius,
            )

            projectile = Tagg(spawn_pos, self.game_objects, lifetime=lifetime, velocity=velocity)
            projectile.set_pos(spawn_pos)
            self.projectiles.add(projectile)

        self.tagg_burst_index += 1

    def start_attack_repeat_cooldown(self, duration):
        self.currentstate.cooldowns.set('tagg_burst_repeat', duration)

    def attack_repeat_ready(self):
        return self.currentstate.cooldowns.get('tagg_burst_repeat') <= 0

    def should_hide_again(self):
        return self.attack_repeat_ready() and self.is_player_close()

    def is_player_close(self):
        player_distance = self.currentstate.player_distance
        aggro_distance = self.config['distances']['aggro']
        return abs(player_distance[0]) < aggro_distance[0] and abs(player_distance[1]) < aggro_distance[1]
