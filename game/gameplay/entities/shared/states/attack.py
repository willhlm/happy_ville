import random
from .base_state import BaseState

class AttackPre(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("attack_pre", 0.25)

    def increase_phase(self):
        self.enter_state("attack_main")

class AttackMain(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("attack_main", 0.2)
        self.entity.attack()

        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack",  random.randint(cooldown[0], cooldown[1]))

    def increase_phase(self):
        self.enter_state("wait", time=10, next_state="chase")
