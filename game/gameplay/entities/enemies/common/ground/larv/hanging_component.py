import math
import random


class HangingComponent:
    def __init__(self, entity, initial_state = None, anchor_pos = None):
        self.entity = entity
        self.anchor_pos = list(anchor_pos or entity.hitbox.center)
        self.initial_state = initial_state
        self.hang_phase = 0
        self.hang_speed = 0
        self.hang_sway_x = 0
        self.hang_sway_y = 0

    def init_motion(self):
        hanging_cfg = self.entity.config['hanging']
        self.hang_phase = random.uniform(0, math.tau)
        self.hang_speed = random.uniform(*hanging_cfg['sway_speed'])
        self.hang_sway_x = random.uniform(*hanging_cfg['sway_x'])
        self.hang_sway_y = random.uniform(*hanging_cfg['sway_y'])

    def enter_initial_state(self):
        if self.initial_state != 'hanging':
            return

        self.entity.set_surface_stick_enabled(False)
        self.entity.body.set_pos([self.anchor_pos[0], self.anchor_pos[1]])
        self.entity.flags['aggro'] = False
        self.entity.currentstate.enter_state('hanging')

    def trigger_drop(self):
        self.entity.set_surface_stick_enabled(False)
        self.entity.currentstate.handle_input('drop')

    def update_hanging_motion(self, dt):
        self.hang_phase += self.hang_speed * dt
        sway_x = math.sin(self.hang_phase) * self.hang_sway_x
        sway_y = math.cos(self.hang_phase * 0.5) * self.hang_sway_y
        self.entity.body.set_pos([
            self.anchor_pos[0] + sway_x,
            self.anchor_pos[1] + sway_y,
        ])
