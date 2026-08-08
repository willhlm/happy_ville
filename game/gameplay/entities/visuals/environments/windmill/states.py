class WindmillState:
    """Base for persistent windmill presentation and future state behaviour."""

    def __init__(self, entity):
        self.entity = entity
        self.angle = 0.0

    def enter_state(self, state_name):
        self.entity.enter_state(state_name)

    def update(self, dt):
        pass

    def handle_input(self, input_name):
        pass

    def increase_phase(self):
        pass


class Idle(WindmillState):
    pass


class Stuck(WindmillState):
    """A failed turn: push against the lock, recoil, then wait to try again."""

    # Durations use the game's update-time units (normally about 60 per second).
    # The deliberate holds and long pause keep this from reading as a pendulum.
    BACKLASH_SEQUENCE = (
        (8.0, 3.0),   # A short attempt to turn the blades.
        (8.0, 6.0),   # The gear catches on the obstruction.
        (-2.5, 2.0),  # Backlash snaps the blades in the opposite direction.
        (0.0, 4.0),   # The mechanism settles back to its resting position.
        (0.0, 30.0),  # Pause before the next failed attempt.
    )

    def __init__(self, entity):
        super().__init__(entity)
        self.time = 0.0

    def update(self, dt):
        self.time = (self.time + dt) % self._cycle_duration()
        elapsed = 0.0
        previous_angle = 0.0

        for target_angle, duration in self.BACKLASH_SEQUENCE:
            if self.time < elapsed + duration:
                progress = (self.time - elapsed) / duration
                self.angle = previous_angle + (target_angle - previous_angle) * progress
                return
            elapsed += duration
            previous_angle = target_angle

        self.angle = 0.0

    @classmethod
    def _cycle_duration(cls):
        return sum(duration for _, duration in cls.BACKLASH_SEQUENCE)


class Active(WindmillState):
    ROTATION_SPEED = 4.0

    def update(self, dt):
        self.angle = (self.angle + self.ROTATION_SPEED * dt) % 360.0


STATE_TYPES = {
    "idle": Idle,
    "stuck": Stuck,
    "active": Active,
}
