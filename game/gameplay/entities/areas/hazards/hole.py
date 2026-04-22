import pygame

from gameplay.entities.shared.components.hazard import VoidHazardComponent

from ..base import BaseArea


class Hole(BaseArea):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.void_hazard = VoidHazardComponent(self)

    def on_collision(self, entity, after_transport=None):
        self.void_hazard.trigger(entity, after_transport=after_transport)
