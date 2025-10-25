import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class Hurt(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("hurt", 0.2)
        self.entity.flags["hurt_able"] = False

        cooldown = self.entity.config["timers"]["hurt_recovery"]        
        self.entity.game_objects.timer_manager.start_timer(random.randint(cooldown[0], cooldown[1]), self.entity.on_hurt_timeout)

    def update_logic(self, dt):
        pass

    def increase_phase(self):
        if random.random() < 0.5:
            self.enter_state("jump_back_pre")
        else:
            self.enter_state("chase")    