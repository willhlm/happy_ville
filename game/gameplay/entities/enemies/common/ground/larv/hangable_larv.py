import math
import random

from gameplay.entities.enemies.base.enemy import Enemy


class HangableLarv(Enemy):
    def __init__(self, pos, game_objects, initial_state = None, anchor_pos = None):
        super().__init__(pos, game_objects)
        self.anchor_pos = list(anchor_pos or pos)
        self._initial_state = initial_state

    def init_hanging_motion(self):
        hanging_cfg = self.config['hanging']
        self.hang_phase = random.uniform(0, math.tau)
        self.hang_speed = random.uniform(*hanging_cfg['sway_speed'])
        self.hang_sway_x = random.uniform(*hanging_cfg['sway_x'])
        self.hang_sway_y = random.uniform(*hanging_cfg['sway_y'])

    def enter_initial_hanging_state(self):
        if self._initial_state != 'hanging':
            return

        self.body.set_pos([self.anchor_pos[0], self.anchor_pos[1]])
        self.flags['aggro'] = False
        self.currentstate.enter_state('hanging')

    def trigger_drop(self):
        self.currentstate.handle_input('drop')
