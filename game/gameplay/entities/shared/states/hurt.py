import random
from .base_state import BaseState

class Hurt(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("hurt", 0.2)
        self.entity.flags["hurt_able"] = False

        cooldown = self.entity.config["timers"]["hurt_recovery"]        
        self.entity.game_objects.timer_manager.start_timer(random.randint(cooldown[0], cooldown[1]), self.entity.on_hurt_timeout)

    def update_logic(self, dt):
        pass

    def increase_phase(self):
        # After hurt animation completes
        self.enter_state("chase")    