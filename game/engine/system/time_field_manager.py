class TimeFieldManager:
    def __init__(self):
        self.fields = []

    def add(self, field):
        self.fields.append(field)

    def remove(self, field):
        if field in self.fields:
            self.fields.remove(field)

    def get_scale_at(self, world_pos):
        scale = 1.0
        for field in self.fields:
            scale = min(scale, field.get_scale_at(world_pos))
        return scale

    def get_dt_at(self, dt, world_pos):
        return dt * self.get_scale_at(world_pos)

class CircularTimeField:
    def __init__(self, center, radius, scale=0.35):
        self.center = list(center)
        self.radius = radius
        self.scale = scale

    def get_scale_at(self, world_pos):
        dx = world_pos[0] - self.center[0]
        dy = world_pos[1] - self.center[1]
        inside = dx * dx + dy * dy <= self.radius * self.radius
        return self.scale if inside else 1.0
