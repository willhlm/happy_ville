from engine.system import animation
from gameplay.entities.platforms.core.platform_entity import PlatformEntity

import traceback

class DynamicPlatform(PlatformEntity):
    def __init__(self, pos, game_objects, size=(16,16), components=None):
        super().__init__(pos, game_objects, size=size)
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
        self.animation.update(dt)

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

    def take_dmg(self, entity):        
        for c in self.components:
            c.take_dmg(entity)        

class _NullState:

    def update(self, dt):
        pass
    
    def increase_phase(self):
        pass        