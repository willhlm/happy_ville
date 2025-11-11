import pygame
from gameplay.entities.projectiles.base.melee import Melee
from gameplay.entities.shared.components import hit_effects

class HurtBox(Melee):#a hitbox that spawns
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = pygame.Rect(entity.rect.topleft, kwarg.get('size', [64, 64]))
        self.base_effect = hit_effects.create_melee_effect(damage = self.dmg, hit_type = 'sword', knockback = [25, 10], hitstop = 10)

    def update_render(self, dt):
        pass

    def update(self, dt):
        self.lifetime -= dt
        self.destroy()

    def draw(self, target):
        pass
