import pygame


class LayeredGroup:
    def __init__(self):
        self.group_dict = {}

    def add(self, layer_name, obj, layer=None):
        self.group_dict[layer_name].add(obj, layer=layer)

    def new_group(self, layer_name, pygame_group):
        self.group_dict[layer_name] = pygame_group

    def draw(self, target):
        for layer, group in self.group_dict.items():
            group.draw(target[layer].layer)

    def empty(self):
        for group in self.group_dict.values():
            group.empty()
        self.group_dict = {}

    def update(self, dt):
        for group in self.group_dict.values():
            group.update(dt)

    def update_render(self, dt):
        for group in self.group_dict.values():
            group.update_render(dt)

    def get_topmost_screen(self):
        return next(reversed(self.group_dict))

    def remove_from_layer(self, layer_name, obj):
        self.group_dict[layer_name].remove(obj)


class LayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()

    def update_render(self, dt):
        for sprite in self.sprites():
            sprite.update_render(dt)

    def update(self, dt):
        from .group_utils import apply_activation

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

