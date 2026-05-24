class LightSync:
    def update(self, light):
        raise NotImplementedError


class FollowTargetSync(LightSync):
    def __init__(self, center_getter):
        self.center_getter = center_getter

    def update(self, light):
        light.hitbox.center = self.center_getter()
        light.sync_render_position()


class StaticPositionSync(LightSync):
    def __init__(self, center_getter):
        self.cached_center = center_getter()

    def update(self, light):
        light.hitbox.center = self.cached_center
        light.sync_render_position()
