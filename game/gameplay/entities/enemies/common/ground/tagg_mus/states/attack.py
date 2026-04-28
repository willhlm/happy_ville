import random

from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_pre")

    def increase_phase(self):
        self.enter_state("attack_main")

class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key,**kwargs):
        super().__init__(entity, deciders,config_key)
        self.entity.animation.play("attack_main")
        self.entity.emit_tagg_burst()
        cooldown_key = kwargs["cooldown"]
        cooldown = self.entity.config["cooldowns"][cooldown_key]
        self.entity.currentstate.cooldowns.set(cooldown_key, random.randint(cooldown[0], cooldown[1]))

    def increase_phase(self):
        self.enter_state("attack_post")

class AttackPost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")

    def increase_phase(self):
        self.enter_state("retreat")
