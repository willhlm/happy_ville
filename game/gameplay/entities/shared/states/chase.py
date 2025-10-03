import random
from .base_state import BaseState
from engine.utils import functions

class Chase(BaseState):
    def __init__(self, entity, deciders, **kwargs):
        super().__init__(entity, deciders)
        self.entity.animation.play("walk")
        self.giveup = kwargs.get("giveup", 400)
        self.time = self.giveup

        cooldown = self.entity.config["cooldowns"]["jump_attack"]
        self.entity.currentstate.cooldowns.set("jump_attack", random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.look_target()
        self.entity.velocity[0] += self.entity.dir[0] * self.entity.chase_speed

    def look_target(self):
        self.entity.dir[0] = functions.sign(self.player_distance[0])