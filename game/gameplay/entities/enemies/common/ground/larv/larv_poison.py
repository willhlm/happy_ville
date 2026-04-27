import pygame

from engine.utils import read_files
from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine import StateManager
from gameplay.entities.projectiles.ranged.poison_blob import PoisonBlob

from .config import ENEMY_CONFIG
from .hanging_component import HangingComponent
from .surface_larv import SurfaceLarv
from .states import AttackMain, AttackPre, Chase, Fall, Hanging, Land, Wait, Hurt

LARV_POISON_STATES = {
    'attack_pre': AttackPre,
    'attack_main': AttackMain,
    'chase': Chase,
    'fall': Fall,
    'hanging': Hanging,
    'land': Land,
    'wait': Wait,
    'hurt': Hurt,    
}

class LarvPoison(SurfaceLarv):
    def __init__(self, pos, game_objects, initial_state = None, anchor_pos = None):
        super().__init__(pos, game_objects)
        self.config = ENEMY_CONFIG['larv_poison']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/larv_poison/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 20, 30)
        self.vitals.set_max_health(self.config['health'])
        self.vitals.set_health(self.vitals.max_health)
        movement_config = self.config['movement']
        if initial_state == 'hanging' or anchor_pos is not None:
            self.hanging_component = HangingComponent(self, initial_state = initial_state, anchor_pos = anchor_pos)
            self.hanging_component.init_motion()
        self.init_surface_stick_motion(
            probe_distance = movement_config['probe_distance'],
            corner_inset = movement_config['corner_inset'],
            enabled = initial_state != 'hanging',
        )

        self.currentstate = StateManager(self, type = 'ground', custom_states = LARV_POISON_STATES, universal_states = ['dead', 'death', 'hurt', 'wait'])
        self.hanging_component.enter_initial_state()

    def attack(self):
        player = self.game_objects.player.hitbox.center
        dx = player[0] - self.hitbox.centerx
        dy = player[1] - self.hitbox.centery
        direction = [-sign(dx) if sign(dx) != 0 else -self.dir[0], sign(dy) if sign(dy) != 0 else 1]
        attack = PoisonBlob(self.rect.topleft, self.game_objects, dir = direction, amp = [4, 4])
        self.game_objects.projectiles.add_enemy(attack)
