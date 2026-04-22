import pygame

from .group_utils import apply_activation


class Group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def update_render(self, dt):
        for sprite in self.sprites():
            sprite.update_render(dt)

    def update(self, dt):
        for sprite in self.sprites():
            sprite.update(dt)
            apply_activation(sprite)

    def draw(self, target):
        for sprite in self.sprites():
            sprite.draw(target)

    def empty(self):
        for sprite in self.sprites():
            sprite.release_texture()
        super().empty()


class CombinedGroup:
    def __init__(self, *groups):
        self._groups = groups

    def sprites(self):
        sprites = []
        for group in self._groups:
            sprites.extend(group.sprites())
        return sprites

    def __iter__(self):
        return iter(self.sprites())

    def __len__(self):
        return len(self.sprites())

