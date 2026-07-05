class Idle:
    def __init__(self, entity, **kwargs):
        self.entity = entity

    def update(self, dt):
        pass


class Grow:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.duration = kwargs.get("duration", 90)
        self.start_edge_falloff_distance = float(kwargs.get('edge_falloff_distance', 3))
        self.target_edge_falloff_distance = float(kwargs.get('target_edge_falloff_distance', 0.12))
        self.entity.edge_falloff_distance = self.start_edge_falloff_distance

    def update(self, dt):
        self.duration -= dt
        self.entity.edge_falloff_distance -= dt * 0.03
        self.entity.edge_falloff_distance = max(self.entity.edge_falloff_distance, self.target_edge_falloff_distance)
        if self.duration <= 0:
            self.entity.enter_state("idle")



STATE_TYPES = {
    "idle": Idle,
    "grow": Grow,
}
