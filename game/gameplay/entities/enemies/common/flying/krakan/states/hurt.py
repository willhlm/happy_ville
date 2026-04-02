import random

from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Hurt(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('hurt', 0.2)
        self.entity.flags['hurt_state_able'] = False

        cooldown = self.entity.config['timers']['hurt_recovery']
        self.entity.game_objects.timer_manager.start_timer(
            random.randint(cooldown[0], cooldown[1]),
            self.entity.on_hurt_timeout
        )

    def update_logic(self, dt):
        if self.entity.collision_types['bottom']:
            self.entity.velocity[0] *= 0.8
            self.entity.velocity[1] = 0
        else:
            self.entity.velocity[1] += dt * self.entity.config['speeds']['landing']

    def increase_phase(self):
        aggro = self.entity.config['distances']['aggro']
        if abs(self.player_distance[0]) < aggro[0] and abs(self.player_distance[1]) < aggro[1]:
            self.enter_state('chase')
        else:
            self.enter_state('patrol')
