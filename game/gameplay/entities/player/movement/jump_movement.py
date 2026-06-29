from engine import constants as C


class JumpMovement:
    def __init__(self, entity):
        self.entity = entity
        self._clear()

    def update(self, dt):
        if not self.active:
            return

        self.timer -= dt
        if self.timer >= 0:
            self.entity.velocity[1] = C.jump_vel_player * self.boost
        else:
            self._clear()

    def start(self, jump_boost=1, air_timer=C.air_timer):
        self.active = True
        self.boost = jump_boost
        self.timer = air_timer
        self.entity.flags['ground'] = False
        self.entity.velocity[1] = C.jump_vel_player * jump_boost

    def extend(self, jump_boost=None, air_timer=None):
        if jump_boost is not None:
            self.boost = jump_boost
            self.entity.velocity[1] = C.jump_vel_player * jump_boost
        if air_timer is not None:
            self.timer = max(self.timer, air_timer)
        self.active = True

    def release(self):
        self._cut_upward_velocity()
        self._clear()

    def interrupt(self):
        self._clear()

    def consume_contact_state(self):
        if self.entity.is_on_ceiling():
            self._clear()
            return

        if self.entity.is_on_floor() and self.entity.velocity[1] >= 0:
            self._clear()

    def _cut_upward_velocity(self):
        if self.entity.velocity[1] < 0:
            self.entity.velocity[1] *= 0.5

    def _clear(self):
        self.active = False
        self.boost = 1
        self.timer = 0
