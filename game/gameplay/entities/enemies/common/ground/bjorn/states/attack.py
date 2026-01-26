import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_pre")

    def increase_phase(self):
        self.enter_state("attack_main")

class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_main")
        self.entity.attack()

        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack",  random.randint(cooldown[0], cooldown[1]))

    def increase_phase(self):
        self.enter_state("attack_post")

class AttackPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")        

    def increase_phase(self):
        self.enter_state("wait", time=10, next_state="chase")        