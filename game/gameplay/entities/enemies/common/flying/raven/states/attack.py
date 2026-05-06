import random
import math

from engine.utils.functions import sign
from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


class AttackPre(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.duration = entity.config['attack']['pre_time']
        self.entity.animation.play('attack_pre', 0.16)
        if 'attack_pre' in self.entity.sounds:
            self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['attack_pre']))

    def update_logic(self, dt):
        self.duration -= dt
        self.entity.velocity[0] *= 0.9
        self.entity.velocity[1] *= 0.9
        if self.duration <= 0:
            self.enter_state('attack_main')


class AttackMain(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.duration = entity.config['attack']['duration']
        self.entity.animation.play('attack_main', 0.22)

        player = entity.game_objects.player.hitbox
        target = [player.centerx, player.centery + 10]
        dx = target[0] - entity.hitbox.centerx
        dy = target[1] - entity.hitbox.centery
        distance = max(1, math.hypot(dx, dy))
        dive_speed = entity.config['speeds']['dive']
        self.dive_velocity = [(dx / distance) * dive_speed, (dy / distance) * dive_speed]

        cooldown = entity.config['cooldowns']['melee_attack']
        entity.currentstate.cooldowns.set('melee_attack', random.randint(cooldown[0], cooldown[1]))

    def update_logic(self, dt):
        self.duration -= dt
        self.entity.velocity[0] = self.dive_velocity[0]
        self.entity.velocity[1] = self.dive_velocity[1]
        if self.dive_velocity[0] != 0:
            self.entity.dir[0] = sign(self.dive_velocity[0])

        if self.entity.is_on_floor() or self.duration <= 0:
            self.enter_state('attack_post')


class AttackPost(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.duration = entity.config['attack']['recover_time']
        self.fall_speed = entity.config['speeds']['fall']
        self.fall_max = entity.config['speeds']['fall_max']
        self.ground_snap = entity.config['speeds']['ground_snap']
        self.entity.animation.play('attack_post', 0.18)

    def update_logic(self, dt):
        self.duration -= dt
        self.entity.velocity[0] *= 0.85
        if self.entity.is_on_floor():
            self.entity.velocity[1] = self.ground_snap
        else:
            self.entity.velocity[1] = min(self.entity.velocity[1] + dt * self.fall_speed, self.fall_max)

        if self.duration <= 0 and self.entity.is_on_floor():
            self.enter_state('patrol')
