import pygame

from gameplay.entities.items.base.entries import InfinityStoneEntry
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.interact_world_item import InteractWorldItem

class InfinityStones(InteractWorldItem):
    item_definition = ItemDefinition(
        item_id='infinity_stone',
        description='Infinity stone',
        pickup_text='Infinity stone',
        pickup_ui_image_path='assets/sprites/ui/overlay/items/placeholder/placeholder.png',
    )
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

    def pickup(self, player):
        self.mark_picked_up()
        copy_item = InfinityStoneEntry.from_item_class(type(self), self.game_objects)
        player.backpack.inventory.add_infinity_stone(copy_item)
        copy_item.attach(player)

    @classmethod
    def entry_on_attach(cls, entry, player):
        pass

    @classmethod
    def pool(cls, game_objects):
        cls.pool_interactable_sprite(game_objects)
        cls.pool_pickup_ui_images(game_objects)
