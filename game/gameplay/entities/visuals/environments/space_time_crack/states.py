import random

class Idle:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def update(self, dt):
        pass

class Grow:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.duration = kwargs.get("duration", 90)
        self.entity.radial_fade_scale = kwargs.get('start_scale', 30)

    def update(self, dt):
        self.duration -= dt
        self.entity.radial_fade_scale -= dt * 0.5
        self.entity.radial_fade_scale = max(self.entity.radial_fade_scale, 1)
        if self.duration <= 0:
            self.entity.enter_state("idle")

class Crack:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.duration = max(float(kwargs.get("duration", 180)), 0.001)
        self.elapsed = 0.0
        self.start_depth = float(kwargs.get("start_depth", entity.crack_depth))
        self.target_depth = float(kwargs.get("target_depth", 6.0))
        self.entity.crack_depth = self.start_depth
        self.entity.game_objects.sound.play_sfx(random.choice(self.entity.sounds['crack']), vol = 0.06)

    def update(self, dt):
        self.elapsed = min(self.elapsed + dt, self.duration)
        progress = self.elapsed / self.duration
        self.entity.crack_depth = self.start_depth + (self.target_depth - self.start_depth) * progress
        if self.elapsed >= self.duration:
            self.entity.enter_state("idle")


STATE_TYPES = {
    "idle": Idle,
    "grow": Grow,
    "crack": Crack,
}
