import math
import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


def _move_towards(entity, target, dt, speed):
    dx = target[0] - entity.hitbox.centerx
    dy = target[1] - entity.hitbox.centery
    distance = math.hypot(dx, dy)
    if distance <= 0:
        return 0

    entity.velocity[0] += dt * (dx / distance) * speed
    entity.velocity[1] += dt * (dy / distance) * speed
    return distance


class Hanging(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.entity.animation.play('hanging', 0.12)

    def update_logic(self, dt):
        self.entity.velocity[0] = 0
        self.entity.velocity[1] = 0

        if (
            abs(self.player_distance[0]) <= self.aggro_distance[0]
            and abs(self.player_distance[1]) <= self.aggro_distance[1]
        ):
            self.enter_state('drop')

    def increase_phase(self):
        pass


class Drop(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.behavior = entity.config['behavior']
        self.drop_target = [
            entity.original_pos[0],
            entity.original_pos[1] + self.behavior['alert_drop_distance'],
        ]
        self.entity.animation.play('drop', 0.14)

    def update_logic(self, dt):
        self.entity.velocity[0] *= 0.85
        self.entity.velocity[1] *= 0.85
        _move_towards(self.entity, self.drop_target, dt, self.behavior['alert_speed'])

        if self.player_distance[0] != 0:
            self.entity.dir[0] = sign(self.player_distance[0]) or self.entity.dir[0]

    def increase_phase(self):
        self.enter_state('alert')


class Alert(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.behavior = entity.config['behavior']
        self.attack_distance = entity.config['distances']['attack']
        self.stop_distance = self.behavior['alert_stop_distance']
        self.entity.animation.play('walk', 0.16)

    def update_logic(self, dt):
        distance = math.hypot(self.player_distance[0], self.player_distance[1])

        if distance > self.stop_distance:
            player = self.entity.game_objects.player.hitbox
            _move_towards(
                self.entity,
                [player.centerx, player.centery],
                dt,
                self.behavior['alert_speed'],
            )
        else:
            self.entity.velocity[0] *= 0.9
            self.entity.velocity[1] *= 0.9

        if self.player_distance[0] != 0:
            self.entity.dir[0] = sign(self.player_distance[0]) or self.entity.dir[0]

        if (
            abs(self.player_distance[0]) <= self.attack_distance[0]
            and abs(self.player_distance[1]) <= self.attack_distance[1]
        ):
            self.enter_state('attack_pre')

    def increase_phase(self):
        pass


class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_pre', 0.18)

    def update_logic(self, dt):
        self.entity.velocity[0] = 0
        self.entity.velocity[1] = 0

    def increase_phase(self):
        self.enter_state('attack_main')


class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.attack_cfg = entity.config['attack']
        self.entity.animation.play('attack_main', 0.18)
        self.shake_timer = 0
        self._reset_attack_timer()
        self._reset_shake_timer()
        self.entity.attack()
        self._shake_camera()
        self.entity.emit_scream_wave()

    def update_logic(self, dt):
        self.entity.velocity[0] = 0
        self.entity.velocity[1] = 0

        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.entity.attack()
            self._reset_attack_timer()

        self.shake_timer -= dt
        if self.shake_timer <= 0:
            self._shake_camera()
            self._reset_shake_timer()

    def increase_phase(self):
        self.entity.animation.play('attack_main', 0.18)

    def _reset_attack_timer(self):
        timer_min, timer_max = self.attack_cfg['crystal_drop_interval']
        self.attack_timer = random.randint(timer_min, timer_max)

    def _reset_shake_timer(self):
        self.shake_timer = self.attack_cfg['scream_shake_interval']

    def _shake_camera(self):
        self.entity.game_objects.camera_manager.camera_shake(
            amplitude=self.attack_cfg['scream_shake_amplitude'],
            duration=self.attack_cfg['scream_shake_duration'],
            scale=self.attack_cfg['scream_shake_scale'],
        )
