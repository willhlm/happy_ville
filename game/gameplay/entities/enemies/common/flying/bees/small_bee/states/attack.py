import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState
from engine.utils.functions import sign

class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_main')     
        self.duration = 50
        distance = (self.entity.currentstate.player_distance[1]**2 + self.entity.currentstate.player_distance[0]**2)**0.5
        if distance == 0: distance = 1
        ratio = [abs(self.player_distance[0])/distance, abs(self.entity.currentstate.player_distance[1])/distance]
        self.velocity = [ratio[0] * 4 * sign(self.entity.currentstate.player_distance[0]), ratio[1] * 4 * sign(self.entity.currentstate.player_distance[1])]

        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack",  random.randint(cooldown[0], cooldown[1]))

    def update(self, dt):
        self.entity.velocity = self.velocity.copy()
        self.duration -= dt
        if self.duration < 0:
            self.enter_state("wait", time=50, next_state="chase")

    def handle_input(self,input):
        if input == 'collision':
            self.enter_state('death')