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

        sprite.game_objects.all_bgs.group_dict[sprite.layer_name].spritedict[sprite] = sprite.game_objects.all_bgs.group_dict[sprite.layer_name]._init_rect
        sprite.game_objects.all_bgs.group_dict[sprite.layer_name]._spritelayers[sprite] = 0
        sprite.game_objects.all_bgs.group_dict[sprite.layer_name]._spritelist.insert(0, sprite)
        sprite.add_internal(sprite.game_objects.all_bgs.group_dict[sprite.layer_name])
        sprite.remove(sprite.pause_group)


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

