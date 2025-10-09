import random
from gameplay.entities.shared.states.enemy.base_state import BaseState

class JumpAttackPre(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("jump_attack_pre")

    def increase_phase(self):
        self.enter_state("jump_attack_main")

class JumpAttackMain(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("jump_attack_main")
        self.entity.velocity[1] = -5

        cooldown = self.entity.config["cooldowns"]["jump_attack"]
        self.entity.currentstate.cooldowns.set("jump_attack", random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.entity.velocity[0] += self.entity.dir[0]
        if self.entity.collision_types["bottom"]:
            self.enter_state("jump_attack_post")

    def modify_hit(self, effect):
        effect.knockback[0] = 0
        return effect

class JumpAttackPost(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("jump_attack_post")

    def increase_phase(self):
        self.enter_state("wait", next_state="chase", time=10)