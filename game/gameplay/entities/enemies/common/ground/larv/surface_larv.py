from engine.utils.functions import sign
from gameplay.entities.enemies.base.enemy import Enemy
from gameplay.entities.shared.components.collision.surface_stick_physics import SurfaceStickPhysics


class SurfaceLarv(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.angle = 0
        self.surface_stick_physics = None
        self.surface_stick_enabled = False
        self.surface_motion_paused = False
        self.surface_freefall_gravity = self.acceleration[1]
        self.hanging_component = None

    def attach_hanging_component(self, component):
        self.hanging_component = component

    def enter_initial_hanging_state(self):
        if self.hanging_component is None:
            return
        self.hanging_component.enter_initial_state()

    def trigger_drop(self):
        if self.hanging_component is None:
            return
        self.hanging_component.trigger_drop()

    def init_surface_stick_motion(
        self,
        *,
        speed,
        stick_speed,
        probe_distance = 2,
        corner_inset = 3,
        clockwise = True,
        initial_side = "bottom",
        enabled = True,
    ):
        self.acceleration[0] = 0
        self.surface_stick_physics = SurfaceStickPhysics(
            self,
            speed = speed,
            stick_speed = stick_speed,
            probe_distance = probe_distance,
            corner_inset = corner_inset,
            clockwise = clockwise,
            initial_side = initial_side,
        )
        self.surface_stick_enabled = enabled
        self.surface_motion_paused = False
        self.angle = self.surface_stick_physics.get_angle()

    def set_surface_stick_enabled(self, enabled = True):
        self.surface_stick_enabled = enabled and self.surface_stick_physics is not None
        self.acceleration[1] = 0 if self.surface_stick_enabled else self.surface_freefall_gravity
        if self.surface_stick_physics is not None:
            self.angle = self.surface_stick_physics.get_angle()

    def uses_surface_stick_motion(self):
        return self.surface_stick_enabled and self.surface_stick_physics is not None

    def set_surface_motion_paused(self, paused = True):
        self.surface_motion_paused = paused

    def reverse_surface_direction(self):
        if self.surface_stick_physics is None:
            self.dir[0] *= -1
            return

        self.surface_stick_physics.clockwise = not self.surface_stick_physics.clockwise

    def set_surface_direction_towards(self, target_pos):
        if self.surface_stick_physics is None:
            desired = sign(target_pos[0] - self.hitbox.centerx)
            if desired:
                self.dir[0] = desired
            return

        dx = target_pos[0] - self.hitbox.centerx
        dy = target_pos[1] - self.hitbox.centery
        side = self.surface_stick_physics.surface_side

        if side == "bottom" and dx != 0:
            self.surface_stick_physics.clockwise = dx > 0
        elif side == "top" and dx != 0:
            self.surface_stick_physics.clockwise = dx < 0
        elif side == "left" and dy != 0:
            self.surface_stick_physics.clockwise = dy > 0
        elif side == "right" and dy != 0:
            self.surface_stick_physics.clockwise = dy < 0

    def update_surface_crawl_state(self, dt, player_distance):
        pass

    def update_vel(self, dt):
        if self.uses_surface_stick_motion():
            if self.surface_motion_paused:
                self.velocity = [0, 0]
                return
            self.surface_stick_physics.update_velocity(dt)
            self.angle = self.surface_stick_physics.get_angle()
            return

        super().update_vel(dt)

    def post_physics_update(self, dt):
        if self.uses_surface_stick_motion():
            dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
            scaled_dt = self.hitstop.get_sim_dt(dt)
            self.surface_stick_physics.post_physics_update(scaled_dt)
            self.angle = self.surface_stick_physics.get_angle()
            self.consume_contact_state()
            self.currentstate.update(scaled_dt)
            self.animation.update(scaled_dt)
            return

        super().post_physics_update(dt)

    def handle_platform_collision(self, collision):
        if self.uses_surface_stick_motion():
            self.surface_stick_physics.handle_platform_collision(collision)
            self.angle = self.surface_stick_physics.get_angle()
            return

        super().handle_platform_collision(collision)

    def draw(self, target):
        blit_pos = [int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]), int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1])]
        self.shader_state.draw(self.image, target, blit_pos, flip = self.dir[0] > 0,  angle = self.angle)


