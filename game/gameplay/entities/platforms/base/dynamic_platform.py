from engine.system import animation
from .platform import Platform

class DynamicPlatform(Platform):
    def __init__(self, pos, game_objects, size=(16,16), components=None):
        super().__init__(pos, size=size)
        self.game_objects = game_objects
        self.velocity = [0.0, 0.0]
        self.delta = [0.0, 0.0]
        self.components = components or []
        self.currentstate = _NullState()
        self.animation = animation.Animation(self)

    # collision dispatch
    def collide_x(self, entity):
        for c in self.components:
            c.collide_x(entity)

    def collide_y(self, entity):
        for c in self.components:
            c.collide_y(entity)

    # per-frame behavior
    def update_components(self, dt):
        for c in self.components:
            c.update(dt)

    def update_render(self, dt):
        pass

    def update(self, dt):
        # 1 — animation/state        
        self.currentstate.update(dt)
        self.animation.update(dt)

        # 3 — components decide motion
        self.update_components(dt)

        # 4 — apply movement
        self.begin_step()
        self.integrate(dt)
        self.end_step()

    def begin_step(self):
        self.old_hitbox = self.hitbox.copy()

    def integrate(self, dt):        
        self.true_pos[0] += dt * self.velocity[0]
        self.true_pos[1] += dt * self.velocity[1]
        self.update_rect_from_true()

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
