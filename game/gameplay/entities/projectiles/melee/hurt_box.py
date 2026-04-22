import pygame
from gameplay.entities.projectiles.base.melee import Melee

class HurtBox(Melee):#a hitbox that spawns
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.hitbox = pygame.Rect(entity.rect.topleft, kwarg.get('size', [64, 64]))
        self.rect.size = self.hitbox.size

    def update_render(self, dt):
        pass

    def draw(self, target):
        pass
