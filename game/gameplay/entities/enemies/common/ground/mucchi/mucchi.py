import pygame

from engine.utils import read_files
from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.shared.components.collision.surface_side import SURFACE_ANGLE_BY_SIDE, SURFACE_BODY_ANCHOR_BY_SIDE
from gameplay.entities.projectiles import HurtBox
from .config import ENEMY_CONFIG as MUCCHI_CONFIG
from .deciders import DirectionalAttackDecider, DirectionalRangeDecider
from .states import AttackMain, AttackPost, AttackPre, Hurt, Idle, Ready

MUCCHI_STATES = {
    'idle': Idle,
    'ready': Ready,
    'hurt': Hurt,
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'attack_post': AttackPost,
}

MUCCHI_DECIDERS = {
    'directional_attack': DirectionalAttackDecider,
    'directional_ready': DirectionalRangeDecider,
    'directional_idle': DirectionalRangeDecider,
}

class Mucchi(Enemy):
    SPRITE_SIZE = (64, 112)
    ROTATED_SPRITE_SIZE = SPRITE_SIZE[::-1]
    HALF_SPRITE_HEIGHT = SPRITE_SIZE[1] * 0.5
    SURFACE_PROFILE_BY_SIDE = {
        'bottom': {
            'attack_direction': (0, 1),
            'visual_size': SPRITE_SIZE,
            'hurtbox_dimensions': ('width', 'reach'),
            'base_from_center': (0, HALF_SPRITE_HEIGHT),
        },
        'top': {
            'attack_direction': (0, -1),
            'visual_size': SPRITE_SIZE,
            'hurtbox_dimensions': ('width', 'reach'),
            'base_from_center': (0, -HALF_SPRITE_HEIGHT),
        },
        'left': {
            'attack_direction': (1, 0),
            'visual_size': ROTATED_SPRITE_SIZE,
            'hurtbox_dimensions': ('reach', 'width'),
            'base_from_center': (-HALF_SPRITE_HEIGHT, 0),
        },
        'right': {
            'attack_direction': (-1, 0),
            'visual_size': ROTATED_SPRITE_SIZE,
            'hurtbox_dimensions': ('reach', 'width'),
            'base_from_center': (HALF_SPRITE_HEIGHT, 0),
        },
    }

    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.config = MUCCHI_CONFIG['mucchi']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/mucchi/', game_objects)
        self.image = self.sprites['idle'][0]

        self.surface_side = str(kwargs.get('surface_side', 'bottom')).strip().lower()
        self.surface_profile = self.SURFACE_PROFILE_BY_SIDE[self.surface_side]
        self.angle = SURFACE_ANGLE_BY_SIDE[self.surface_side]
        self.dir = list(self.surface_profile['attack_direction'])
        # Convert the engine's up-positive direction to screen coordinates.
        self.attack_vector = (self.dir[0], -self.dir[1])
        body_anchor = SURFACE_BODY_ANCHOR_BY_SIDE[self.surface_side]
        self.surface_anchor = tuple(kwargs.get('surface_anchor',(pos[0] + self.SPRITE_SIZE[0] * 0.5,pos[1] + self.SPRITE_SIZE[1])))

        self.rect = self._make_visual_bounds(body_anchor)
        self.hitbox = pygame.Rect(0, 0, 32, 32)
        setattr(self.hitbox, body_anchor, self.surface_anchor)
        self.body.anchor = body_anchor
        self.true_pos = list(self.rect.topleft)
        self.platform_collider.enabled = False

        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        self.currentstate = StateManager(self, type='ground', custom_states=MUCCHI_STATES, custom_deciders=MUCCHI_DECIDERS, universal_states=['death', 'dead', 'hurt'])

    def _make_visual_bounds(self, anchor):
        rect = pygame.Rect(0, 0, *self.surface_profile['visual_size'])
        setattr(rect, anchor, self.surface_anchor)
        return rect

    def attack(self):
        hurtbox = self.config['hurtbox']
        size = [hurtbox[dimension] for dimension in self.surface_profile['hurtbox_dimensions']]

        attack = HurtBox(self, lifetime=10, dir=self.dir, size=size)
        self.game_objects.projectiles.add_enemy(attack)

    def update_vel(self, dt):
        self.velocity = [0, 0]

    def knock_back(self, amp, dir):
        pass

    def draw(self, target):
        width, height = self.SPRITE_SIZE
        base_from_center = self.surface_profile['base_from_center']
        center = (self.surface_anchor[0] - base_from_center[0], self.surface_anchor[1] - base_from_center[1])
        position = [
            int(center[0] - width * 0.5 - self.game_objects.camera_manager.camera.scroll[0]),
            int(center[1] - height * 0.5 - self.game_objects.camera_manager.camera.scroll[1]),
        ]
        self.shader_state.draw(self.image, target, position, angle=self.angle)
