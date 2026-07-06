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



STATE_TYPES = {
    "idle": Idle,
    "grow": Grow,
}
