import math
import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


def _move_towards(entity, target, dt, speed):
    dx = target[0] - entity.hitbox.centerx
    dy = target[1] - entity.hitbox.centery
    distance = math.hypot(dx, dy)
    if distance <= 0.001:
        return 0

    entity.velocity[0] += dt * (dx / distance) * speed
    entity.velocity[1] += dt * (dy / distance) * speed
    return distance


class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_pre', 0.1)
        self.hover = entity.config['hover']
        self.attack = entity.config['attack']
        self.line_up_speed = self.attack['line_up_speed']
        side = -sign(self.player_distance[0]) if self.player_distance[0] != 0 else -self.entity.dir[0]
        target_y = kwargs.get('target_y', self.entity.game_objects.player.hitbox.centery - self.hover['height'])
        self.target_position = [
            self.entity.game_objects.player.hitbox.centerx + side * self.hover['side_offset'],
            target_y,
        ]
        self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['attack_pre']))

    def update_logic(self, dt):
        self.entity.dir[0] = sign(self.player_distance[0]) if self.player_distance[0] != 0 else self.entity.dir[0]
        _move_towards(self.entity, self.target_position, dt, self.line_up_speed)

    def increase_phase(self):
        self.enter_state('attack_main')


class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_main', 0.22)
        self.duration = 55

        player = self.entity.game_objects.player.hitbox
        target = [player.centerx, player.centery + 12]
        dx = target[0] - self.entity.hitbox.centerx
        dy = target[1] - self.entity.hitbox.centery
        distance = max(1, math.hypot(dx, dy))
        dive_speed = self.entity.config['speeds']['dive']
        self.dive_velocity = [(dx / distance) * dive_speed, (dy / distance) * dive_speed]

        cooldown = self.entity.config['cooldowns']['melee_attack']
        self.entity.currentstate.cooldowns.set('melee_attack', random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.duration -= dt
        self.entity.dir[0] = sign(self.dive_velocity[0]) if self.dive_velocity[0] != 0 else self.entity.dir[0]
        self.entity.velocity[0] = self.dive_velocity[0]
        self.entity.velocity[1] = self.dive_velocity[1]

        if self.duration <= 0:
            self.enter_state('attack_post')

class AttackPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_post', 0.2)
        self.attack = entity.config['attack']
        self.retreat_speed = self.attack['retreat_speed']
        self.retreat_time = self.attack['retreat_time']

        retreat_dir = -sign(self.player_distance[0]) if self.player_distance[0] != 0 else -self.entity.dir[0]
        player = self.entity.game_objects.player.hitbox
        self.retreat_target = [
            player.centerx + retreat_dir * self.attack['retreat_distance'],
            player.centery - self.attack['retreat_height'],
        ]

    def update_logic(self, dt):
        self.retreat_time -= dt
        self.entity.dir[0] = sign(self.player_distance[0]) if self.player_distance[0] != 0 else self.entity.dir[0]
        distance = _move_towards(self.entity, self.retreat_target, dt, self.retreat_speed)
        if self.retreat_time <= 0 or distance < 18:
            if self._player_in_range():
                self.enter_state('chase')
            else:
                self.enter_state('patrol')

    def _player_in_range(self):
        aggro = self.entity.config['distances']['aggro']
        return abs(self.player_distance[0]) < aggro[0] and abs(self.player_distance[1]) < aggro[1]
