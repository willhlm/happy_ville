import random
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.velocity = [0, 0]
        self.entity.animation.play("attack_pre", 0.25)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("attack_main")


class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.velocity = [0, 0]
        self.entity.animation.play("attack_main", 0.2)
        self.entity.attack()

        cooldown = self.entity.config["cooldowns"]["surface_attack"]
        self.entity.currentstate.cooldowns.set("surface_attack", random.randint(cooldown[0], cooldown[1]))

    def increase_phase(self):
        self.enter_state("crawl")

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]
