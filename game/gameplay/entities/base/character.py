from engine import constants as C

from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.hit.hit_component import HitComponent
from gameplay.entities.shared.components.collision.platform_physics import PlatformPhysics
from gameplay.entities.shared.modifiers import modifier_movement
from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager

class Character(AnimatedEntity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = {'ramp': True, 'one_way':True}
        self.velocity = [0, 0]
        self.body = EntityBody(self)
        self.movement_manager = modifier_movement.MovementManager(self)
        self.platform_physics = PlatformPhysics(self)
        self.hitstop = HitstopComponent()
        self.standing_platform = None
        self.acceleration = [0, C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()

        self.shader_state = EntityShaderManager(self)
        self.hit_component = HitComponent(self)

    def update(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)

        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)

        self.movement_manager.update(scaled_dt)
        self.update_vel(scaled_dt)
        self.currentstate.update(scaled_dt)#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update(scaled_dt)#need to be after currentstate since animation will animate the current state

    def update_render(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.shader_state.update_render(scaled_dt)

    def update_vel(self, dt):#called from hitsop_states
        context = self.movement_manager.resolve()

        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]#gravity
        self.velocity[1] = min(self.velocity[1], context.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0] * self.acceleration[0] - context.friction[0] * self.velocity[0]) + context.velocity[0]

    def take_hit(self, effect):
        """Delegate to hit component"""
        return self.hit_component.take_hit(effect)

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        self.health -= effect.damage

        if self.health > 0:  # Still alive
            self.shader_state.handle_input('Hurt')
            self.currentstate.handle_input('Hurt')
            self.game_objects.camera_manager.camera_shake(amplitude=4, duration=12, scale=0.9)
        else:  # dead
            self.game_objects.camera_manager.camera_shake(amplitude=4, duration=20, scale=0.95)
            self.flags['aggro'] = False
            self.currentstate.die()
        return effect

    def knock_back(self, amp, dir):
        self.velocity[0] = dir[0] * amp[0]
        self.velocity[1] = -dir[1] * amp[1]

    def on_ramp_collision(self, side, ramp):
        if side == 'bottom':
            self.currentstate.handle_input('Ground')
            self.standing_platform = ramp

    def on_platform_side_collision(self, side, block, collision_type = 'Wall'):
        self.currentstate.handle_input(collision_type)

    def on_platform_vertical_collision(self, side, block):
        if side == 'bottom':
            self.currentstate.handle_input('Ground')
            self.standing_platform = block
        else:
            self.velocity[1] = 0
            self.currentstate.handle_input('ceiling')

    def on_limit_y(self):
        self.velocity[1] = 1.2#assume at least 60 fps -> 1

    def on_crush(self, block):
        self.currentstate.die()

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
