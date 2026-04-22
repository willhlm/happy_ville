from gameplay.entities.platforms.base.platform import Platform
from gameplay.entities.platforms.components.surface_collision import OneWayUpSurfaceCollisionComponent


class OneWayUpPlatform(Platform):
    def __init__(self, pos, size=(16, 16), run_particle='dust'):
        super().__init__(pos, size=size, run_particle=run_particle)
        self.surface_collision = OneWayUpSurfaceCollisionComponent(self)
