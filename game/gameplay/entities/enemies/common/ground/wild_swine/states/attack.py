import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState
from gameplay.entities.projectiles import HurtBox

class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_pre", f_rate = 0.2)
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("charging")

    def handle_input(self, input_type):
        pass

class Charging(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("walk", 0.17)
        self.charge_speed = self.entity.config['speeds']['charge']
        self.commit_distance = self.entity.config['distances']['charge_commit']
        self.charge_dir = self.entity.dir[0]

    def update_logic(self, dt):
        player_dx = self.player_distance[0]
        player_dir = 1 if player_dx >= 0 else -1
        self.entity.dir[0] = self.charge_dir
        self.entity.velocity[0] += dt * self.charge_dir * self.charge_speed

        if player_dir != self.charge_dir:
            self.enter_state("attack_main")
            return

        if abs(player_dx) <= self.commit_distance[0] and abs(self.player_distance[1]) <= self.commit_distance[1]:
            self.enter_state("attack_main")

    def handle_input(self, input_type):
        pass

class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_main")
        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack", random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.entity.velocity[0] += dt * self.entity.dir[0] * self.entity.config['speeds']['charge']

    def handle_input(self, input_type):
        if input_type == "Wall":
            self.entity.velocity[0] = 0
            self.entity.game_objects.camera_manager.camera_shake(duration=15)
            self.increase_phase()
            return

    def increase_phase(self):
        self.enter_state("attack_post")

class AttackPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("attack_post")

    def increase_phase(self):
        self.enter_state("wait", time=20, next_state="chase")

    def handle_input(self, input_type):
        pass