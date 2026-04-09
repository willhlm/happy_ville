import math
import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


def _play_animation(entity, name, rate = 0.2):
    if entity.animation.animation_name != name:
        entity.animation.play(name, rate)


def _move_towards(entity, target, dt, speed):
    dx = target[0] - entity.hitbox.centerx
    dy = target[1] - entity.hitbox.centery
    distance = math.hypot(dx, dy)
    if distance <= 0.001:
        return 0

    entity.velocity[0] += dt * (dx / distance) * speed
    entity.velocity[1] += dt * (dy / distance) * speed
    return distance


class Patrol(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.behavior = entity.config['behavior']
        self.home_radius = self.behavior['home_radius']
        self.ground_speed = entity.config['speeds']['ground']
        self.landing_speed = entity.config['speeds']['landing']
        self.landing_max = entity.config['speeds']['landing_max']
        self.ground_snap = entity.config['speeds']['ground_snap']
        self.takeoff_speed = entity.config['speeds']['takeoff']
        self.ground_leash = self.behavior['ground_leash']
        self.grounded_timer = 0
        self.ground_action_time = 0
        self.ground_action_dir = 0

    def update_logic(self, dt):
        if self._player_in_range() and self._player_in_home_zone():
            self.enter_state('chase')
            return

        if self.entity.is_on_floor():
            self.grounded_timer = self.behavior['grounded_grace_time']
        else:
            self.grounded_timer = max(0, self.grounded_timer - dt)

        if self.grounded_timer > 0:
            self.entity.velocity[1] = self.ground_snap
            self._perch(dt)
            return

        _play_animation(self.entity, 'fly', 0.18)
        drift = self.entity.original_pos[0] - self.entity.hitbox.centerx
        self.entity.velocity[0] += dt * sign(drift) * self.ground_speed * 0.35
        self.entity.velocity[1] = min(self.entity.velocity[1] + dt * self.landing_speed, self.landing_max)

    def _perch(self, dt):
        drift = self.entity.original_pos[0] - self.entity.hitbox.centerx
        if abs(drift) > self.ground_leash:
            self.entity.dir[0] = sign(drift)
            _play_animation(self.entity, 'walk', 0.18)
            self.entity.velocity[0] += dt * self.entity.dir[0] * self.ground_speed
            self.ground_action_time = 0
            self.ground_action_dir = 0
            return

        self.ground_action_time -= dt
        if self.ground_action_time <= 0:
            self.ground_action_time = random.randint(*self.behavior['ground_wander_time'])
            if random.random() < self.behavior['ground_wander_chance']:
                self.ground_action_dir = random.choice([-1, 1])
            else:
                self.ground_action_dir = 0

        if self.ground_action_dir != 0:
            self.entity.dir[0] = self.ground_action_dir
            _play_animation(self.entity, 'walk', 0.18)
            self.entity.velocity[0] += dt * self.ground_action_dir * self.ground_speed * 0.65
        else:
            _play_animation(self.entity, 'idle', 0.16)
            self.entity.velocity[0] *= 0.8

    def _player_in_range(self):
        return (
            abs(self.player_distance[0]) < self.aggro_distance[0]
            and abs(self.player_distance[1]) < self.aggro_distance[1]
        )

    def _player_in_home_zone(self):
        player = self.entity.game_objects.player.hitbox
        return (
            abs(player.centerx - self.entity.original_pos[0]) < self.home_radius[0]
            and abs(player.centery - self.entity.original_pos[1]) < self.home_radius[1]
        )


class Chase(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.attack_distance = entity.config['distances']['attack']
        self.behavior = entity.config['behavior']
        self.home_radius = self.behavior['home_radius']
        self.chase_speed = entity.config['speeds']['chase']
        self.takeoff_speed = entity.config['speeds']['takeoff']
        self.give_up_timer = self.behavior['give_up_time']
        self.hover_target_y = self._clamp_target_y(self.entity.game_objects.player.hitbox.centery - self.behavior['hover_height'])
        self.hover_phase = 0 if self.player_distance[0] >= 0 else math.pi
        self.hover_bob_phase = random.uniform(0, math.tau)
        self.prev_hover_sign = sign(math.sin(self.hover_phase))
        self.turns_before_attack = random.randint(*self.behavior['attack_turns'])
        self.completed_crosses = 0

    def update_logic(self, dt):
        if not self._player_in_range():
            self.give_up_timer -= dt
            if self.give_up_timer <= 0:
                self.enter_state('patrol')
                return
        else:
            self.give_up_timer = self.behavior['give_up_time']

        self._update_hover_target_y(dt)
        self._update_hover_phase(dt)

        if self._ready_to_dive() and self._player_in_home_zone() and self._completed_turns() >= self.turns_before_attack:
            self.enter_state('attack_pre', target_y = self.hover_target_y)
            return

        hover_offset_x = math.sin(self.hover_phase) * self.behavior['hover_span']
        hover_offset_y = math.sin(self.hover_bob_phase) * self.behavior['hover_bob_height']
        desired_position = [
            self.entity.game_objects.player.hitbox.centerx + hover_offset_x,
            self._clamp_target_y(self.hover_target_y + hover_offset_y),
        ]
        desired_position[0] = max(self.entity.original_pos[0] - self.home_radius[0], min(desired_position[0], self.entity.original_pos[0] + self.home_radius[0]))

        _play_animation(self.entity, 'fly', 0.2)
        horizontal_travel = desired_position[0] - self.entity.hitbox.centerx
        if abs(horizontal_travel) > 2:
            self.entity.dir[0] = sign(horizontal_travel)
        _move_towards(self.entity, desired_position, dt, self.chase_speed)

    def _player_in_range(self):
        return (
            abs(self.player_distance[0]) < self.aggro_distance[0]
            and abs(self.player_distance[1]) < self.aggro_distance[1]
        )

    def _player_in_home_zone(self):
        player = self.entity.game_objects.player.hitbox
        return (
            abs(player.centerx - self.entity.original_pos[0]) < self.home_radius[0]
            and abs(player.centery - self.entity.original_pos[1]) < self.home_radius[1]
        )

    def _ready_to_dive(self):
        return (
            abs(self.player_distance[0]) < self.attack_distance[0]
            and self.entity.currentstate.cooldowns.get('melee_attack') <= 0
        )

    def _update_hover_target_y(self, dt):
        desired_y = self._clamp_target_y(self.entity.game_objects.player.hitbox.centery - self.behavior['hover_height'])
        delta = desired_y - self.hover_target_y
        if abs(delta) <= self.behavior['hover_vertical_deadzone']:
            return

        step = min(abs(delta), self.behavior['hover_follow_speed'] * dt)
        self.hover_target_y += sign(delta) * step

    def _clamp_target_y(self, value):
        return max(
            self.entity.original_pos[1] - self.home_radius[1],
            min(value, self.entity.original_pos[1] + self.home_radius[1])
        )

    def _update_hover_phase(self, dt):
        self.hover_phase += self.behavior['hover_cross_speed'] * dt
        self.hover_bob_phase += self.behavior['hover_bob_speed'] * dt
        hover_sign = sign(math.sin(self.hover_phase))
        if hover_sign == 0:
            return
        if self.prev_hover_sign == 0:
            self.prev_hover_sign = hover_sign
            return
        if hover_sign != self.prev_hover_sign:
            self.completed_crosses += 1
            self.prev_hover_sign = hover_sign

    def _completed_turns(self):
        return self.completed_crosses // 2
