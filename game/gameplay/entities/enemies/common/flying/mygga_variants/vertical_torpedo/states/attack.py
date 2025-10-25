# orthogonal_torpedo/states/attack.py
import random
from gameplay.entities.enemies.common.shared.states.base_state import BaseState
from engine.utils.functions import sign

class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_main')
        self.duration = 50
        
        # Torpedo downward toward player
        self.velocity = [0, 0]
        self.velocity[0] = 0
        self.velocity[1] = 4  # Fast downward
        
        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack", random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.entity.velocity = self.velocity.copy()
        self.duration -= dt
        if self.duration < 0:
            self.enter_state("wait", time=50, next_state="chase")