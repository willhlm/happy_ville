import random
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class Hurt(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        # Mucchi has no separate hurt animation; the shader supplies the hit
        # feedback while this short state prevents it from attacking.
        self.entity.animation.play('idle', 0.2)
        self.entity.flags['hurt_state_able'] = False
        self.time = self.entity.config['timers']['hurt_stun']

        cooldown = self.entity.config['timers']['hurt_recovery']
        self.entity.game_objects.timer_manager.start_timer(random.randint(cooldown[0], cooldown[1]), self.entity.on_hurt_timeout)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
        self.time -= dt
        if self.time <= 0:
            self.enter_state('idle')

    def increase_phase(self):
        pass
