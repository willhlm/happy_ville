import random
from .base_state import BaseState

class Hurt(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("hurt", 0.2)
        self.entity.flags["hurt_state_able"] = False#a flag to check if it can enter state

        cooldown = self.entity.config["timers"]["hurt_recovery"]        
        self.entity.game_objects.timer_manager.start_timer(random.randint(cooldown[0], cooldown[1]), self.entity.on_hurt_timeout)

    def update_logic(self, dt):
        pass

    def increase_phase(self):# After hurt animation completes  
        states = self.entity.config.get('states', {})
        hurt_cfg = states.get('hurt', {})

        next_state = hurt_cfg.get('next_state', 'chase')
        kwargs = hurt_cfg.get('kwargs', {})

        self.enter_state(next_state, **kwargs)