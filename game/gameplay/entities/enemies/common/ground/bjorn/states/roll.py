import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState

class RollAttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("roll_attack_pre")

    def increase_phase(self):
        self.enter_state("roll_attack_main")

class RollAttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("roll_attack_main")
        self.entity.velocity[1] = -5

        self.dir = self.entity.dir.copy()

        self.number_bounce = 5
        self.request_bounce = False

    def update_logic(self, dt):
        self.entity.velocity[0] += self.dir[0] * 2
        if self.request_bounce:
            self.entity.velocity[1] = -8# bounce
            self.request_bounce = False

    def handle_input(self, input):   
        if input == 'Ground':
            self.request_bounce = True            
            self.number_bounce -= 1
            if self.number_bounce <= 0:
                self.enter_state("roll_attack_post")
        elif input == 'ceiling':
            self.dir[1] = 1
        elif input == 'Wall':
            if self.entity.collision_types['left']:
                self.dir[0] = 1            
            else:
                self.dir[0] = -1

class RollAttackPost(BaseState):
    def __init__(self, entity, deciders,config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("roll_attack_post")
        cooldown = self.entity.config["cooldowns"]["roll_attack"]
        self.entity.currentstate.cooldowns.set("roll_attack", random.randint(cooldown[0], cooldown[1]))

    def increase_phase(self):
        self.enter_state("wait", next_state="chase", time=10)