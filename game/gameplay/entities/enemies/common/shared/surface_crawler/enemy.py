from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.common.surface_side import SURFACE_BODY_ANCHOR_BY_SIDE, get_surface_draw_flip
from gameplay.entities.shared.components.collision.surface_stick_physics import NullSurfaceStickPhysics, SurfaceStickPhysics


class NullHangingComponent:
    def init_motion(self):
        return None

    def enter_initial_state(self):
        return None

    def trigger_drop(self):
        return None

    def update_hanging_motion(self, dt):
        return None


class SurfaceCrawlerEnemy(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.angle = 0
        self.surface_stick_physics = NullSurfaceStickPhysics(self)
        self.hanging_component = NullHangingComponent()

    def init_surface_stick_motion(
        self,
        *,
        probe_distance = 2,
        corner_inset = 3,
        clockwise = True,
        initial_side = "bottom",
        enabled = True,
    ):
        self.acceleration[0] = 0
        self.surface_stick_physics = SurfaceStickPhysics(
            self,
            probe_distance = probe_distance,
            corner_inset = corner_inset,
            clockwise = clockwise,
            initial_side = initial_side,
        )
        self.surface_stick_physics.set_enabled(enabled)
        self.sync_surface_orientation()

    def uses_surface_stick_motion(self):
        return self.surface_stick_physics.is_enabled()

    def sync_surface_angle(self):
        self.angle = self.surface_stick_physics.get_angle()

    def sync_surface_body_anchor(self):
        surface_side = self.surface_stick_physics.surface_side
        anchor = SURFACE_BODY_ANCHOR_BY_SIDE[surface_side]
        if self.body.anchor == anchor:
            return

        self.body.anchor = anchor
        setattr(self.rect, anchor, getattr(self.hitbox, anchor))
        self.true_pos = list(self.rect.topleft)

    def sync_surface_orientation(self):
        self.sync_surface_angle()
        self.sync_surface_body_anchor()

    def update_surface_stick_motion(self):
        self.surface_stick_physics.update_surface()
        self.sync_surface_orientation()

    def post_surface_stick_motion(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.surface_stick_physics.post_physics_update(scaled_dt)
        self.sync_surface_orientation()
        self.consume_contact_state()
        self.currentstate.update(scaled_dt)
        self.animation.update(scaled_dt)

    def handle_surface_stick_collision(self, collision):
        self.surface_stick_physics.handle_platform_collision(collision)
        self.sync_surface_orientation()

    def apply_surface_move_velocity(self, speed = None, stick_speed = None):
        if not self.uses_surface_stick_motion():
            return

        movement_config = self.config.get("movement", {})
        if speed is None:
            speed = movement_config.get("crawl_speed", self.config["speeds"]["crawl"])
        if stick_speed is None:
            stick_speed = movement_config.get("stick_speed", 0)

        tangent = self.surface_stick_physics.get_tangent_vector()
        inward = self.surface_stick_physics.get_inward_vector()

        self.velocity[0] = tangent[0] * speed + inward[0] * stick_speed
        self.velocity[1] = tangent[1] * speed + inward[1] * stick_speed

        if tangent[0] != 0:
            self.dir[0] = 1 if tangent[0] > 0 else -1

    def update_vel(self, dt):
        if not self.uses_surface_stick_motion():
            super().update_vel(dt)
            return

        self.update_surface_stick_motion()

    def post_physics_update(self, dt):
        if not self.uses_surface_stick_motion():
            super().post_physics_update(dt)
            return

        self.post_surface_stick_motion(dt)

    def handle_platform_collision(self, collision):
        if not self.uses_surface_stick_motion():
            super().handle_platform_collision(collision)
            return

        self.handle_surface_stick_collision(collision)

    def get_surface_draw_flip(self):
        if not self.uses_surface_stick_motion():
            return self.dir[0] > 0

        tangent = self.surface_stick_physics.get_tangent_vector()
        return get_surface_draw_flip(self.surface_stick_physics.surface_side, tangent)

    def draw(self, target):
        blit_pos = [int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]), int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1])]
        self.shader_state.draw(self.image, target, blit_pos, flip = self.get_surface_draw_flip(), angle = self.angle)
