from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState
from .helpers import (
    get_tagg_burst_repeat_cooldown,
)

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
        self.entity.material = 'metal'
        self.has_emitted_burst = False

    def increase_phase(self):
        pass

    def update_logic(self, dt):
        if self.has_emitted_burst:
            return

        self.entity.emit_tagg_burst()
        self.has_emitted_burst = True
        self.entity.start_attack_repeat_cooldown(get_tagg_burst_repeat_cooldown(self.entity))
        self.enter_state("attack_post")

class AttackPost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")
        self.entity.material = 'flesh'

    def increase_phase(self):
        self.enter_state("retreat")
