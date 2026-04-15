import pygame

from gameplay.entities.items.base.entries import InfinityStoneEntry
from gameplay.entities.items.base.components import ItemInteractComponent, pool_interactable_sprite, InteractionPickupComponent
from gameplay.entities.items.base.world_item import WorldItem

class InfinityStones(WorldItem):
    pickup_component_cls = InteractionPickupComponent

    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.interact_component = ItemInteractComponent(self, **kwarg)
        self.description = ''

    def pickup(self, player):
        self.mark_picked_up()
        copy_item = InfinityStoneEntry.from_item_class(type(self), self.game_objects)
        player.backpack.inventory.add_infinity_stone(copy_item)
        copy_item.attach(player)

    def interact(self, player):
        self.interact_component.interact_with_pickup_text(player)

    @classmethod
    def entry_on_attach(cls, entry, player):
        pass

    @classmethod
    def pool(cls, game_objects):
        pool_interactable_sprite(cls, game_objects)
