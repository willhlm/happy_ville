import pygame
from gameplay.entities.projectiles.base.melee import Melee

class Hurt_box(Melee):#a hitbox that spawns
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = pygame.Rect(entity.rect.topleft, kwarg.get('size', [64, 64]))
        self.dmg = kwarg.get('dmg', 1)

    def update_render(self, dt):
        pass

    def update(self, dt):
        self.lifetime -= dt
        self.destroy()

    def draw(self, target):
        pass
