from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState
from .helpers import get_retreat_time


class Retreat(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("walk", 0.17)
        self.retreat_time = get_retreat_time(entity)
        self.retreat_speed = entity.config['speeds']['retreat']
        self.aggro_distance = entity.config['distances']['aggro']

        player_dx = self.player_distance[0]
        self.entity.dir[0] = -1 if player_dx >= 0 else 1

    def update_logic(self, dt):
        if not self.is_player_close():
            self.enter_state("patrol", dir=self.entity.dir[0])
            return

        player_dx = self.player_distance[0]
        self.entity.dir[0] = -1 if player_dx >= 0 else 1

        if self.retreat_time > 0:
            self.retreat_time -= dt

        self.entity.velocity[0] += dt * self.entity.dir[0] * self.retreat_speed

    def is_player_close(self):
        player_distance = self.player_distance
        
        return abs(player_distance[0]) < self.aggro_distance[0] and abs(player_distance[1]) < self.aggro_distance[1]
