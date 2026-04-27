import math
import random

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState

class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_pre', 0.24)
        self.time_left = self.entity.config['behavior']['attack_pre_time']

    def update_logic(self, dt):
        self.time_left -= dt
        self.entity.velocity[0] *= 0.88
        self.entity.velocity[1] *= 0.88
        if self.time_left <= 0:
            self.enter_state('attack_main')

    def increase_phase(self):
        self.enter_state('attack_main')

class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play('attack_main')
        self.duration = 44
        distance = math.hypot(self.player_distance[0], self.player_distance[1])
        if distance == 0:
            distance = 1

        attack_speed = self.entity.config['speeds']['attack']
        self.velocity = [
            (self.player_distance[0] / distance) * attack_speed + self.entity.swarm_attack_jitter[0],
            (self.player_distance[1] / distance) * attack_speed + self.entity.swarm_attack_jitter[1],
        ]

        cooldown = self.entity.config['cooldowns']['melee_attack']
        self.entity.currentstate.cooldowns.set('melee_attack', random.randint(cooldown[0], cooldown[1]))
        self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['attack']))

    def update(self, dt):
        self.entity.dir[0] = sign(self.velocity[0]) if self.velocity[0] != 0 else self.entity.dir[0]
        self.entity.velocity = self.velocity.copy()
        self.duration -= dt
        if self.duration < 0:
            self.enter_state(
                'wait',
                time=random.randint(*self.entity.config['behavior']['post_attack_delay']),
                next_state='chase',
            )

    def handle_input(self, input_type):
        if input_type == 'collision':
            self.enter_state('death')
