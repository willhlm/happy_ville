import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

from .common import player_in_range


class GroundIdle(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.patrol = entity.config['patrol']
        self.home_radius = self.patrol['home_radius']
        self.ground_snap = entity.config['speeds']['ground_snap']
        self.ground_leash = self.patrol['ground_leash']
        self.ground_action_time = kwargs.get('time', 0)
        self.entity.animation.play('idle', 0.16)

    def update_logic(self, dt):
        self.entity.velocity[0] = 0
        if player_in_range(self, self.aggro_distance):
            self.enter_state('chase')
            return

        if not self.entity.is_on_floor():
            self.enter_state('air_patrol')
            return

        drift = self.entity.original_pos[0] - self.entity.hitbox.centerx
        if abs(drift) > self.ground_leash:
            self.enter_state('ground_walk', dir = sign(drift))
            return

        self.ground_action_time -= dt
        if self.ground_action_time <= 0:
            self.ground_action_time = random.randint(*self.patrol['wander_time'])
            if random.random() < self.patrol['wander_chance']:
                self.enter_state(
                    'ground_walk',
                    dir = random.choice([-1, 1]),
                    time = self.ground_action_time,
                )
                return
        
class GroundWalk(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.aggro_distance = entity.config['distances']['aggro']
        self.patrol = entity.config['patrol']
        self.home_radius = self.patrol['home_radius']
        self.ground_speed = self.patrol['ground_speed']
        self.ground_snap = entity.config['speeds']['ground_snap']
        self.ground_leash = self.patrol['ground_leash']
        self.walk_dir = kwargs.get('dir', entity.dir[0] or 1)
        self.walk_time = kwargs.get('time', 0)
        self.entity.animation.play('walk', 0.18)

    def update_logic(self, dt):
        if player_in_range(self, self.aggro_distance):
            self.enter_state('chase')
            return

        if not self.entity.is_on_floor():
            self.enter_state('air_patrol')
            return

        self.entity.velocity[1] = self.ground_snap
        drift = self.entity.original_pos[0] - self.entity.hitbox.centerx
        if abs(drift) > self.ground_leash:
            self.walk_dir = sign(drift)

        self.walk_time -= dt
        if self.walk_time <= 0 and abs(drift) <= self.ground_leash:
            self.enter_state('patrol')
            return

        self.entity.dir[0] = self.walk_dir        
        speed_scale = 1 if abs(drift) > self.ground_leash else 0.65
        self.entity.velocity[0] += dt * self.walk_dir * self.ground_speed * speed_scale
