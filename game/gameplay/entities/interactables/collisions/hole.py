import pygame
from .base_collisions import BaseCollisions

class Hole(BaseCollisions):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen

    def on_collision(self, entity, after_transport=None):
        if self.game_objects.transition.is_busy:
            return
        if hasattr(entity, 'hazard_resolver'):#player
            entity.hazard_resolver.handle_void(self, after_transport=after_transport)
        else:
            entity.currentstate.die()

