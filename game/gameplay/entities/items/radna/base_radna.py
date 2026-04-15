from gameplay.entities.items.base.entries import RadnaEntry
from gameplay.entities.items.base.components import ItemInteractComponent, pool_interactable_sprite, InteractionPickupComponent
from gameplay.entities.items.base.world_item import WorldItem

class Radna(WorldItem):
    inventory_level = 1
    inventory_description = ''
    pickup_component_cls = InteractionPickupComponent

    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.interact_component = ItemInteractComponent(self, **kwarg)
        self.description = type(self).inventory_description
        self.level = type(self).inventory_level#the level of ring reuried to equip

    def pickup(self, player):
        self.mark_picked_up()
        copy_item = RadnaEntry.from_item_class(type(self), self.game_objects)
        player.backpack.radna.add(copy_item)
        self.game_objects.signals.emit('item_interacted', item = self, player = player)
        self.kill()

    def interact(self, player):
        self.interact_component.interact_with_pickup_text(player)

    @classmethod
    def entry_update_equipped(cls, entry):
        pass

    @classmethod
    def entry_on_handle_press_input(cls, entry, input):
        pass

    @classmethod
    def entry_on_attach(cls, entry):
        pass

    @classmethod
    def entry_on_detach(cls, entry):
        pass

    @classmethod
    def pool(cls, game_objects):
        pool_interactable_sprite(cls, game_objects)
