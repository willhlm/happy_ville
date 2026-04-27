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


def _update_flying_buzz(state, dt):
    state.flying_buzz_timer -= dt
    if state.flying_buzz_timer > 0:
        return

    speed = abs(state.entity.velocity[0]) + abs(state.entity.velocity[1])
    vol_min, vol_max = state.entity.flying_buzz_volume
    volume = min(vol_max, vol_min + speed * 0.015)
    state.entity.game_objects.sound.play_spatial_sfx(
        random.choice(state.entity.sounds['flying']),
        point=state.entity.hitbox.center,
        vol=volume,
        min_dist=48,
        max_dist=600,
    )
    state.flying_buzz_timer = random.randint(*state.entity.flying_buzz_interval)

class Patrol(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('walk', 0.22)
        self.aggro_distance = entity.config['distances']['aggro']
        self.patrol_speed = entity.config['speeds']['patrol']
        self.behavior = entity.config['behavior']
        self.phase = entity.swarm_seed
        self.flying_buzz_timer = random.randint(8, 28)
        self._choose_target()

    def update_logic(self, dt):
        if self._player_in_range():
            self.enter_state('chase')
            return

        distance = _move_towards(self.entity, self.target_position, dt, self.patrol_speed)
        self.phase += self.behavior['swarm_weave_speed'] * 0.7 * dt
        self.entity.velocity[1] += math.sin(self.phase) * 0.003 * dt
        _update_flying_buzz(self, dt)
        if distance < 12:
            self._choose_target()

    def _choose_target(self):
        radius_x, radius_y = self.behavior['patrol_radius']
        angle = random.uniform(0, math.tau)
        self.target_position = [
            self.entity.original_pos[0] + math.cos(angle) * radius_x,
            self.entity.original_pos[1] + math.sin(angle) * radius_y,
        ]
        self.entity.dir[0] = sign(self.target_position[0] - self.entity.hitbox.centerx) or self.entity.dir[0]

    def _player_in_range(self):
        return (
            abs(self.player_distance[0]) < self.aggro_distance[0]
            and abs(self.player_distance[1]) < self.aggro_distance[1]
        )


class Chase(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('walk', 0.24)
        self.behavior = entity.config['behavior']
        self.aggro_distance = entity.config['distances']['aggro']
        self.attack_distance = entity.config['distances']['attack']
        self.swarm_speed = entity.config['speeds']['swarm']
        self.give_up_timer = self.behavior['give_up_time']
        self.attack_commit_timer = entity.swarm_attack_commit
        self.phase = entity.swarm_seed
        self.flying_buzz_timer = random.randint(8, 28)

    def update_logic(self, dt):
        if not self._player_in_range():
            self.give_up_timer -= dt
            if self.give_up_timer <= 0:
                self.enter_state('patrol')
                return
        else:
            self.give_up_timer = self.behavior['give_up_time']

        self.phase += self.behavior['swarm_weave_speed'] * dt
        target_position = self._swarm_target()
        distance = _move_towards(self.entity, target_position, dt, self.swarm_speed)
        _update_flying_buzz(self, dt)

        horizontal_travel = target_position[0] - self.entity.hitbox.centerx
        if abs(horizontal_travel) > 2:
            self.entity.dir[0] = sign(horizontal_travel)

        close_enough = distance < self.behavior['charge_release_distance'] or abs(self.player_distance[0]) < self.attack_distance[0]
        if close_enough and self.entity.currentstate.cooldowns.get('melee_attack') <= 0:
            self.attack_commit_timer -= dt
            if self.attack_commit_timer <= 0:
                self.enter_state('attack_pre')
                return
        else:
            self.attack_commit_timer = self.entity.swarm_attack_commit

    def _swarm_target(self):
        player = self.entity.game_objects.player.hitbox
        return [
            player.centerx + self.entity.swarm_side_bias * self.entity.swarm_side_offset + math.sin(self.phase) * self.behavior['swarm_weave_x'],
            player.centery + self.entity.swarm_height_offset + math.cos(self.phase * 1.3) * self.behavior['swarm_weave_y'],
        ]

    def _player_in_range(self):
        return (
            abs(self.player_distance[0]) < self.aggro_distance[0]
            and abs(self.player_distance[1]) < self.aggro_distance[1]
        )
