import pygame

from .base_entry import ItemEntry


class InfinityStoneEntry(ItemEntry):
    def __init__(self, item_cls, game_objects, description, animation_name):
        super().__init__(item_cls, game_objects, description, animation_name)
        self.shader = None
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)

    @classmethod
    def from_item_class(cls, item_cls, game_objects):
        animation_name = cls._resolve_animation_name(item_cls)
        description = item_cls.get_item_definition().description
        return cls(item_cls, game_objects, description, animation_name)

    def set_pos(self, pos):
        self.rect.center = pos

    def attach(self, player):
        handler = getattr(self.item_cls, 'entry_on_attach', None)
        if handler:
            handler(self, player)
