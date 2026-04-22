from engine.system import animation
from .platform import Platform
from gameplay.entities.shared.components.body.entity_body import EntityBody

class DynamicPlatform(Platform):
    def __init__(self, pos, game_objects, size=(16,16), components=None):
        super().__init__(pos, size=size)
        self.game_objects = game_objects
        self.body = EntityBody(self, anchor='topleft')
        self.old_hitbox = self.hitbox.copy()
        self.velocity = [0.0, 0.0]
        self.delta = [0.0, 0.0]
        self.components = components or []
        self.currentstate = _NullState()
        self.animation = animation.Animation(self)

    def get_support_motion(self, entity):
        for c in self.components:
            motion = c.get_support_motion(entity)
            if motion is not None:
                return motion
        return None

    def get_floor_samples(self, entity):
        samples = []
        for component in self.components:
            samples.extend(component.get_floor_samples(entity))
        return samples or super().get_floor_samples(entity)

    def get_ceiling_samples(self, entity):
        samples = []
        for component in self.components:
            samples.extend(component.get_ceiling_samples(entity))
        return samples or super().get_ceiling_samples(entity)

    def get_wall_samples(self, entity):
        samples = []
        for component in self.components:
            samples.extend(component.get_wall_samples(entity))
        return samples or super().get_wall_samples(entity)

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        for component in self.components:
            component.on_platform_collision(entity, side, axis, collision_kind)

    def supports_drop_through(self, entity, probe_hitbox):
        for component in self.components:
            target = component.supports_drop_through(entity, probe_hitbox)
            if target is not None:
                return target
        return super().supports_drop_through(entity, probe_hitbox)

    # per-frame behavior
    def update_components(self, dt):
        for c in self.components:
            c.update(dt)

    def update_render(self, dt):
        pass

    def update(self, dt):
        dt = self.game_objects.time_field_manager.get_dt_at(dt, self.hitbox.center)

        # 1 — animation/state                
        self.currentstate.update(dt)
        self.animation.update(dt)

        # 2 — subclass motion
        self.update_vel(dt)

        # 3 — components decide motion
        self.update_components(dt)

        # 4 — apply movement
        self.begin_step()
        self.integrate(dt)
        self.end_step()

    def begin_step(self):
        self.old_hitbox = self.hitbox.copy()

    def update_vel(self, dt):
        pass

    def integrate(self, dt):
        self.body.update_true_pos_x(dt)
        self.body.update_true_pos_y(dt)

    def end_step(self):
        self.delta[0] = self.hitbox.left - self.old_hitbox.left
        self.delta[1] = self.hitbox.top  - self.old_hitbox.top        

    def reset_timer(self):
        self.currentstate.increase_phase()

    def take_hit(self, effect):
        effect.attacker_callbacks.pop('hitstop', None)
        effect.defender_callbacks.pop('visual', None)#depends on if we want shader state
        effect.defender_callbacks.pop('hitstop', None)
        effect.defender_callbacks.pop('particles', None)
        effect.attacker_callbacks.pop('sword_jump', None)
        return self.hit_component.take_hit(effect)

    def take_dmg(self, effect):#called from hit copmentn
        for component in self.components:
            effect = component.take_dmg(effect)
        return effect

class _NullState:

    def update(self, dt):
        pass
    
    def increase_phase(self):
        pass        
