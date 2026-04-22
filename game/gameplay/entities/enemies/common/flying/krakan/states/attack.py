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
        self.entity.animation.play('attack_pre', 0.22)
        self.behavior = entity.config['behavior']
        self.line_up_speed = entity.config['speeds']['line_up']
        self.time_left = self.behavior['attack_pre_time']
        self.commit_distance = self.behavior['attack_commit_distance']
        side = -sign(self.player_distance[0]) if self.player_distance[0] != 0 else -self.entity.dir[0]
        target_y = kwargs.get('target_y', self.entity.game_objects.player.hitbox.centery - self.behavior['hover_height'])
        self.target_position = [
            self.entity.game_objects.player.hitbox.centerx + side * self.behavior['hover_side_offset'],
            target_y,
        ]

    def update_logic(self, dt):
        self.time_left -= dt
        self.entity.dir[0] = sign(self.player_distance[0]) if self.player_distance[0] != 0 else self.entity.dir[0]
        _move_towards(self.entity, self.target_position, dt, self.line_up_speed)

        dx = abs(self.target_position[0] - self.entity.hitbox.centerx)
        dy = abs(self.target_position[1] - self.entity.hitbox.centery)
        if self.time_left <= 0 or (dx <= self.commit_distance[0] and dy <= self.commit_distance[1]):
            self.enter_state('attack_main')

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

    def handle_input(self, input_type):
        if input_type in ('Ground', 'Wall', 'ceiling'):
            self.enter_state('attack_post')
            return
        super().handle_input(input_type)


class AttackPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_post', 0.2)
        self.behavior = entity.config['behavior']
        self.retreat_speed = entity.config['speeds']['retreat']
        self.retreat_time = self.behavior['retreat_time']

        retreat_dir = -sign(self.player_distance[0]) if self.player_distance[0] != 0 else -self.entity.dir[0]
        player = self.entity.game_objects.player.hitbox
        self.retreat_target = [
            player.centerx + retreat_dir * self.behavior['retreat_distance'],
            player.centery - self.behavior['retreat_height'],
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
