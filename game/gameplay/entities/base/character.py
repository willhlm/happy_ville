from engine import constants as C

from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.hit.hit_component import HitComponent
from gameplay.entities.shared.components.collision.contact_state import ContactState
from gameplay.entities.shared.components.collision.platform_collider import PlatformCollider
from gameplay.entities.shared.components.vitals.vitals_component import VitalsComponent
from gameplay.entities.shared.modifiers import modifier_movement
from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager

class Character(AnimatedEntity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.contact_state = ContactState()
        self.go_through = {'drop_through': True}
        self.velocity = [0, 0]
        self.body = EntityBody(self)
        self.movement_manager = modifier_movement.MovementManager(self)
        self.platform_collider = PlatformCollider(self)
        self.hitstop = HitstopComponent()
        self.acceleration = [0, C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()
        self._movement_context = modifier_movement.MovementContext(self)

        self.shader_state = EntityShaderManager(self)
        self.hit_component = HitComponent(self)
        self.vitals = VitalsComponent(self)

    def update(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)

        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)

        self.movement_manager.update(scaled_dt)
        self.update_vel(scaled_dt)

    def post_physics_update(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.consume_contact_state()
        self.currentstate.update(scaled_dt)
        self.animation.update(scaled_dt)

    def update_render(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.shader_state.update_render(scaled_dt)

    def update_vel(self, dt):#called from hitsop_states
        context = self.movement_manager.resolve()
        self._movement_context = context

        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]#gravity
        self.velocity[1] = min(self.velocity[1], context.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0] * self.acceleration[0] - context.friction[0] * self.velocity[0]) + context.velocity[0]

    def take_hit(self, effect):
        """Delegate to hit component"""
        return self.hit_component.take_hit(effect)

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        self.vitals.damage(effect.damage)

        if self.vitals.health > 0:  # Still alive
            self.shader_state.handle_input('Hurt')
            self.currentstate.handle_input('Hurt')
            self.game_objects.camera_manager.camera_shake(amplitude=4, duration=12, scale=0.9)
        else:  # dead
            self.game_objects.camera_manager.camera_shake(amplitude=4, duration=20, scale=0.95)
            self.currentstate.die()
        return effect

    def knock_back(self, amp, dir):
        self.velocity[0] = dir[0] * amp[0]
        self.velocity[1] = -dir[1] * amp[1]

    def apply_ground_snap_velocity(self):
        self.velocity[1] = 1.2#assume at least 60 fps -> 1

    def on_crush(self, block):
        self.currentstate.die()

    def consume_contact_state(self):
        self.consume_contact_effects()
        self.consume_platform_collisions()
        self.currentstate.consume_contact_state()

    def consume_contact_effects(self):
        for collision in self.contact_state.collisions:
            collision.contact_effect.apply(self)

    def consume_platform_collisions(self):
        for collision in self.contact_state.collisions:
            self.handle_platform_collision(collision)

    def handle_platform_collision(self, collision):
        if collision.axis == 'y' and collision.side != 'bottom':
            self.velocity[1] = 0

    def is_on_floor(self):
        return self.contact_state.is_on_floor()

    def has_ground_grace(self):
        return self.is_on_floor() or self.was_on_floor()

    def is_on_wall(self):
        return self.contact_state.is_on_wall()

    def is_on_wall_side(self, side):
        return self.contact_state.has_side(side)

    def is_on_ceiling(self):
        return self.contact_state.is_on_ceiling()

    def get_floor_normal(self):
        return self.contact_state.get_floor_normal()

    def get_wall_normal(self):
        return self.contact_state.get_wall_normal()

    def get_surface_normal(self):
        return self.contact_state.get_surface_normal()

    def get_slide_collision_count(self):
        return self.contact_state.get_slide_collision_count()

    def get_slide_collision(self, index):
        return self.contact_state.get_slide_collision(index)

    def has_collision_side(self, side):
        return self.contact_state.has_side(side)

    def get_collisions_for_side(self, side):
        return self.contact_state.get_collisions_for_side(side)

    def has_collision_kind(self, collision_kind, side=None):
        return self.contact_state.has_collision_kind(collision_kind, side=side)

    def get_real_velocity(self, dt):
        return self.contact_state.get_real_velocity(dt)

    def get_motion_remainder(self):
        return self.contact_state.motion_result.remainder

    def get_motion_travel(self):
        return self.contact_state.motion_result.travel

    def was_on_floor(self):
        return self.contact_state.was_on_floor

    def was_on_wall(self):
        return self.contact_state.was_on_wall

    def was_on_ceiling(self):
        return self.contact_state.was_on_ceiling

    def get_previous_surface_normal(self):
        return self.contact_state.previous_surface_normal

    def get_support_body(self):
        return self.contact_state.support_body

    def get_previous_support_body(self):
        return self.contact_state.previous_support_body

    def should_apply_support_motion(self, axis, amount):
        if amount == 0:
            return False

        if axis == 'y':
            return True

        return not self._movement_context.lock_support_axes[0]

    def get_support_contact_tolerance(self):
        return 1

    def draw(self, target):
        blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.shader_state.draw(self.image, target, blit_pos, flip = self.dir[0] > 0)

    def on_attack_timeout(self):#when attack cooldown timer runs out
        self.flags['attack_able'] = True

    def on_hurt_timeout(self):#starts when entering hurt state, and make sure that you don't eneter again until timer runs out
        self.flags['hurt_state_able'] = True

    def release_texture(self):#called when .kill() and empty group
        self.shader_state.clear_textures()   
        super().release_texture()        
