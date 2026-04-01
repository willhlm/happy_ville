from gameplay.entities.projectiles.base.projectile_base import ProjectileBase
from gameplay.entities.shared.components.collision.platform_physics import PlatformPhysics


class PlatformProjectile(ProjectileBase):
    uses_platform_physics = True

    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.go_through = {'ramp': True, 'one_way': True}
        self.platform_physics = PlatformPhysics(self)
        self.standing_platform = None

    def on_ramp_collision(self, side, ramp):
        pass

    def on_platform_side_collision(self, side, block, collision_type='Wall'):
        pass

    def on_platform_vertical_collision(self, side, block):
        pass

    def on_limit_y(self):
        pass

    def on_crush(self, block):
        self.kill()
