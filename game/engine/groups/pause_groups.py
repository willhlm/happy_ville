import pygame


class PauseLayer(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def update(self, dt):
        for sprite in self.sprites():
            self.group_distance(sprite)

    def empty(self):
        for sprite in self.sprites():
            sprite.release_texture()
        super().empty()

    @staticmethod
    def group_distance(sprite):
        if not sprite.game_objects.activation_manager.is_active(sprite):
            return
        sprite.game_objects.activation_manager.wake(sprite)


class PauseGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def update(self, dt):
        for sprite in self.sprites():
            self.group_distance(sprite)

    def empty(self):
        for sprite in self.sprites():
            sprite.release_texture()
        super().empty()

    @staticmethod
    def group_distance(sprite):
        if not sprite.game_objects.activation_manager.is_active(sprite):
            return
        sprite.game_objects.activation_manager.wake(sprite)
