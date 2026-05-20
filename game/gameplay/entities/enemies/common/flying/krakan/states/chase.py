import math
import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

from .common import steer_towards


class Chase(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.attack_distance = entity.config['distances']['attack']
        self.patrol = entity.config['patrol']
        self.hover = entity.config['hover']
        self.attack = entity.config['attack']
        self.home_radius = self.patrol['home_radius']
        self.chase_speed = entity.config['speeds']['chase']
        self.give_up_timer = self.attack['give_up_time']
        self.hover_phase = 0 if self.player_distance[0] >= 0 else math.pi
        self.prev_hover_sign = sign(math.cos(self.hover_phase))
        self.turns_before_attack = random.randint(*self.attack['turns_before_dive'])
        self.completed_crosses = 0
        self.turn_threshold = 0.04
        self._apply_takeoff_impulse()
        self.entity.animation.play('fly', 0.2)
        self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['alert']))

        self.sound_timer = 10

    def _play_sounds(self, dt):
        self.sound_timer -= dt
        if self.sound_timer <= 0:
            self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['fly']), vol = 0.2)
            self.sound_timer = 30

    def update_logic(self, dt):
        self._play_sounds(dt)

        if not self._player_in_range():
            self.give_up_timer -= dt
            if self.give_up_timer <= 0:
                self.enter_state('patrol')
                return
        else:
            self.give_up_timer = self.attack['give_up_time']

        self._update_hover_phase(dt)
        orbit_anchor = self._get_orbit_anchor()

        if self._ready_to_dive() and self._completed_turns() >= self.turns_before_attack:
            self.enter_state('attack_pre', target_y = orbit_anchor[1])
            return

        hover_offset_x = math.cos(self.hover_phase) * self.hover['orbit_radius_x']
        hover_offset_y = math.sin(self.hover_phase) * self.hover['orbit_radius_y']
        desired_position = [
            orbit_anchor[0] + hover_offset_x,
            orbit_anchor[1] + hover_offset_y,
        ]
        
        self._move_chase(desired_position, orbit_anchor, dt)
        if abs(self.entity.velocity[0]) > self.turn_threshold:
            self.entity.dir[0] = sign(self.entity.velocity[0])

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
            abs(self.player_distance[1]) < self.attack_distance[1]
            and self.entity.currentstate.cooldowns.get('melee_attack') <= 0
        )

    def _get_orbit_anchor(self):
        player = self.entity.game_objects.player.rect
        anchor_x = self._clamp_target_x(player.centerx)
        anchor_y = self._clamp_target_y(player.centery - self.hover['height'])
        return [anchor_x, anchor_y]

    def _clamp_target_x(self, value):
        return max(
            self.entity.original_pos[0] - self.home_radius[0],
            min(value, self.entity.original_pos[0] + self.home_radius[0])
        )

    def _clamp_target_y(self, value):
        return max(
            self.entity.original_pos[1] - self.home_radius[1],
            min(value, self.entity.original_pos[1] + self.home_radius[1])
        )

    def _update_hover_phase(self, dt):
        self.hover_phase += self.hover['cross_speed'] * dt
        hover_sign = sign(math.cos(self.hover_phase))
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

    def _move_chase(self, desired_position, orbit_anchor, dt):
        if self._is_below_hover_band(orbit_anchor):
            # During takeoff/climb, bias toward getting above the player first.
            # Full orbit sway should only happen once Krakan has reached hover height.
            climb_target = [orbit_anchor[0], orbit_anchor[1]]
            steer_towards(
                self.entity,
                climb_target,
                dt,
                self.patrol['takeoff_rise_speed'],
                response = self.patrol['takeoff_rise_response'],
                slow_radius = 8,
            )
            return

        steer_towards(self.entity, desired_position, dt, self.chase_speed)

    def _is_below_hover_band(self, orbit_anchor):
        return self.entity.hitbox.centery > orbit_anchor[1] + self.patrol['takeoff_end_height']

    def _apply_takeoff_impulse(self):
        if not self.entity.is_on_floor():
            return

        self.entity.velocity[1] = min(self.entity.velocity[1], -self.patrol['takeoff_boost'])
        launch_dir = sign(self.player_distance[0]) if self.player_distance[0] != 0 else self.entity.dir[0]
        self.entity.velocity[0] += launch_dir * self.patrol['takeoff_forward_boost']
