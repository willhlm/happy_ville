from gameplay.entities.projectiles.base.projectile_base import ProjectileBase
from gameplay.entities.shared.components.collision.contact_state import ContactState
from gameplay.entities.shared.components.collision.platform_collider import PlatformCollider
from gameplay.entities.shared.components.collision.surface_attachment import NullSurfaceAttachment, SurfaceAttachment

class PlatformProjectile(ProjectileBase):
    uses_platform_collider = True
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.contact_state = ContactState()
        self.go_through = {'drop_through': True}
        self.platform_collider = PlatformCollider(self)
        self.surface_attachment = NullSurfaceAttachment(self)

    def update(self, dt):
        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.projectile_clash.update(scaled_dt)
        
        self.currentstate.update(scaled_dt)
        self.animation.update(scaled_dt)   

        self.body.update_true_pos_x(scaled_dt)
        self.body.update_true_pos_y(scaled_dt)

        self.lifetime -= scaled_dt
        self.destroy()    

    def apply_ground_snap_velocity(self):
        pass

    def on_crush(self, block):
        self.kill()

    def post_physics_update(self, dt):
        self.consume_contact_effects()
        self.consume_platform_collisions()
        self.surface_attachment.post_physics_update(dt)

    def consume_contact_effects(self):
        for collision in self.contact_state.collisions:
            collision.contact_effect.apply(self)

    def consume_platform_collisions(self):
        for collision in self.contact_state.collisions:
            self.handle_platform_collision(collision)

    def handle_platform_collision(self, collision):
        return

    def enable_surface_attachment(self):
        if isinstance(self.surface_attachment, NullSurfaceAttachment):
            self.surface_attachment = SurfaceAttachment(self)

    def disable_surface_attachment(self):
        self.surface_attachment.detach()
        self.surface_attachment = NullSurfaceAttachment(self)

    def is_attached_to_surface(self):
        return self.surface_attachment.is_attached()

    def attach_to_surface(self, collision):
        self.enable_surface_attachment()
        return self.surface_attachment.attach_from_collision(collision)

    def on_projectile_reflected(self, other, direction, position, team=None, clamp_value=10):
        if team is not None and team != self.team:
            self.game_objects.projectiles.route(self, team)

        dy = max(-clamp_value, min(clamp_value, self.rect.centery - position[1]))
        dx = max(-clamp_value, min(clamp_value, self.rect.centerx - position[0]))

        if dir[1] != 0:
            self.velocity[0] = dx * 0.2
            self.velocity[1] = -10 * dir[1]
        else:
            self.velocity[0] = 10 * dir[0]
            self.velocity[1] = dy * 0.2        
