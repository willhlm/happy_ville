import pygame
from gameplay.entities.base.static_entity import StaticEntity

class Stop(StaticEntity):
    def __init__(self, game_objects, size, pos, mode, offset=0, priority=0):
        super().__init__(pos, game_objects)
        self.size = size
        self.rect[2], self.rect[3] = size[0], size[1]
        self.hitbox = pygame.Rect(pos, size)
        self.mode = str(mode).lower()
        self.offset = int(offset)
        self.priority = int(priority)

    def release_texture(self):#called when .kill() and empty group
        pass

    def update(self, dt):
        pass

    def is_active(self, player):
        activation = self.hitbox.inflate(self.offset * 32, self.offset * 32)
        return activation.colliderect(player.hitbox)

    @property
    def area(self):
        return self.hitbox[2] * self.hitbox[3]
