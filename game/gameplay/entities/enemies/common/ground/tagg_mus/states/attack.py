from gameplay.entities.enemies.common.shared.states.base_state import BaseState
from .helpers import (
    get_player_aligned_burst_offset,
    get_tagg_burst_chain_cooldown,
    get_tagg_burst_profile,
    get_tagg_burst_repeat_cooldown,
    get_tagg_burst_volley_count,
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
        self.burst_cooldown = 0
        self.bursts_remaining = get_tagg_burst_volley_count(entity)

    def increase_phase(self):
        pass

    def update_logic(self, dt):
        self.burst_cooldown -= dt
        if self.burst_cooldown > 0:
            return

        burst_count, burst_speed = get_tagg_burst_profile(self.entity)
        angle_offset = get_player_aligned_burst_offset(self.entity, burst_count)
        self.entity.emit_tagg_burst(angle_offset=angle_offset, count=burst_count, speed=burst_speed)

        self.bursts_remaining -= 1
        if self.bursts_remaining > 0:
            self.burst_cooldown = get_tagg_burst_chain_cooldown(self.entity)
            return

        self.entity.start_attack_repeat_cooldown(get_tagg_burst_repeat_cooldown(self.entity))
        self.enter_state("attack_post")

class AttackPost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")
        self.entity.material = 'flesh'

    def increase_phase(self):
        self.enter_state("retreat")
