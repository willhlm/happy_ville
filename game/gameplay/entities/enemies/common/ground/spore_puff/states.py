import random
from engine.utils.functions import sign

from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


def _play_state_animation(entity, state_name, speed=0.2, fallback="idle"):
    animation_name = state_name if state_name in entity.sprites else fallback
    entity.animation.play(animation_name, speed)


class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_pre", 0.25)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("attack_main")


class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_main", 0.2)
        self.entity.attack()

        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack", random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("attack_post")


class AttackPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post", 0.2)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("wait", time=10, next_state="patrol")


class Seed(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.flags['aggro'] = False
        _play_state_animation(self.entity, "seed")
        self.save = self.entity.friction[0]
        self.entity.friction[0] = 0

    def update_logic(self, dt):
        if self.entity.is_on_floor() and self.entity.velocity[1] >= 0:
            self.entity.velocity = [0, 0]
            self.entity.friction[0] = self.save
            self.enter_state("grow")

class Grow(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.flags['aggro'] = False
        self.entity.velocity = [0, 0]
        _play_state_animation(self.entity, "grow")

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("plant")


class Plant(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.flags['aggro'] = False
        self.entity.velocity = [0, 0]
        self.time = kwargs.get("time", 140)
        _play_state_animation(self.entity, "plant")

    def update(self, dt):
        self.time -= dt
        if self.time <= 0:
            self.enter_state("spawn")

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]


class Spawn(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.flags['aggro'] = False
        self.entity.velocity = [0, 0]
        _play_state_animation(self.entity, "spawn")

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.entity.flags['aggro'] = True
        self.enter_state("patrol")
