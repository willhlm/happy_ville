import random

from gameplay.entities.enemies.common.shared.state_machine.states.base_state import BaseState


def _choose_horizontal_dir(entity):
    horizontal_range = entity.config['movement']['horizontal_range']
    offset_x = entity.hitbox.centerx - entity.original_pos[0]
    if offset_x > horizontal_range:
        return -1
    if offset_x < -horizontal_range:
        return 1
    return random.choice([-1, 1])


class Accend(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("accend", 0.2)
        self.time = self.entity.config['movement']['accend_time']
        self.duration = self.time
        self.vertical_speed = self.entity.config['speeds']['accend']
        self.horizontal_speed = self.entity.config['speeds']['horizontal']
        self.horizontal_dir = _choose_horizontal_dir(self.entity)
        self.entity.dir[0] = self.horizontal_dir
        self.entity.set_accend_light()

    def update_logic(self, dt):
        self.entity.velocity[0] = self.horizontal_dir * self.horizontal_speed
        self.entity.velocity[1] = -self.vertical_speed
        self.time -= dt
        if self.time <= 0:
            self.enter_state("deccend", horizontal_dir=self.horizontal_dir)


class Deccend(BaseState):
    def __init__(self, entity, deciders, config_key, **kwargs):
        super().__init__(entity, deciders, config_key)
        self.entity.animation.play("deccend", 0.2)
        self.time = self.entity.config['movement']['deccend_time']
        self.duration = self.time
        self.vertical_speed = self.entity.config['speeds']['deccend']
        self.horizontal_speed = self.entity.config['speeds']['horizontal']
        self.horizontal_dir = kwargs.get('horizontal_dir', _choose_horizontal_dir(self.entity))
        self.entity.dir[0] = self.horizontal_dir

    def update_logic(self, dt):
        self.entity.velocity[0] = self.horizontal_dir * self.horizontal_speed
        self.entity.velocity[1] = self.vertical_speed
        self.time -= dt
        progress = 1.0 - (self.time / self.duration if self.duration > 0 else 1.0)
        self.entity.update_deccend_light(progress)
        if self.time <= 0:
            self.enter_state("accend")
