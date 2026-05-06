import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

from .common import move_towards


class Chase(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.hover_cfg = entity.config['hover']
        self.aggro_distance = entity.config['distances']['aggro']
        self.attack_distance = entity.config['distances']['attack']
        self.takeoff_speed = entity.config['speeds']['takeoff']
        self.hover_speed = entity.config['speeds']['hover']
        self.hover_timer = self.hover_cfg['attack_delay']
        self.entity.animation.play('fly', 0.18)
        if 'alert' in self.entity.sounds:
            self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['alert']))

    def update_logic(self, dt):
        hover_target = self._get_hover_target()
        distance = move_towards(
            self.entity,
            hover_target,
            dt,
            self.takeoff_speed if self._is_below_hover_target(hover_target) else self.hover_speed,
        )

        if abs(self.entity.velocity[0]) > 0.05:
            self.entity.dir[0] = sign(self.entity.velocity[0])
        elif self.player_distance[0] != 0:
            self.entity.dir[0] = sign(self.player_distance[0])

        if self._can_start_dive(distance):
            self.hover_timer -= dt
            if self.hover_timer <= 0:
                self.enter_state('attack_pre')
        else:
            self.hover_timer = self.hover_cfg['attack_delay']

    def _get_hover_target(self):
        player = self.entity.game_objects.player.hitbox
        side = -sign(self.player_distance[0]) if self.player_distance[0] != 0 else -self.entity.dir[0]
        return [
            player.centerx + side * self.hover_cfg['side_offset'],
            player.centery - self.hover_cfg['height'],
        ]

    def _is_below_hover_target(self, hover_target):
        return self.entity.hitbox.centery > hover_target[1] + self.hover_cfg['align_padding']

    def _can_start_dive(self, distance):
        if self.entity.currentstate.cooldowns.get('melee_attack') > 0:
            return False

        return (
            abs(self.player_distance[0]) < self.attack_distance[0]
            and abs(self.player_distance[1]) < self.attack_distance[1]
            and distance < self.hover_cfg['align_padding']
        )
