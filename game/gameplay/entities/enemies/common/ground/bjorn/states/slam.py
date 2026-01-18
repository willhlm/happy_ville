import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class SlamPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("slam_pre")

    def increase_phase(self):
        self.enter_state("slam_main")

class SlamMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("slam_main")
        self.entity.slam()

        cooldown = self.entity.config["cooldowns"]["slam_attack"]
        self.entity.currentstate.cooldowns.set("slam_attack",  random.randint(cooldown[0], cooldown[1]))

    def increase_phase(self):
        self.enter_state("slam_post")

class SlamPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("slam_post")        

    def increase_phase(self):
        self.enter_state("wait", time=10, next_state="chase")        