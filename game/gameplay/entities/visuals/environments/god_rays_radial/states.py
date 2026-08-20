class Idle:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def update(self, dt):
        pass


class Grow:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.duration = kwargs.get("duration", 90)
        self.radius = float(kwargs.get('radius', 0))
        self.target_radius = float(kwargs.get('target_radius', 1))
        self.entity.radius = self.radius
        self.speed = float(kwargs.get('speed', 0.01))

    def update(self, dt):
        self.duration -= dt
        self.entity.radius += dt * self.speed
        self.entity.radius = min(self.entity.radius, self.target_radius)
        if self.duration <= 0:
            self.entity.enter_state("idle")



STATE_TYPES = {
    "idle": Idle,
    "grow": Grow,
}
