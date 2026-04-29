from gameplay.entities.items.base.entries import RadnaEntry
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.base.interact_world_item import InteractWorldItem

class Radna(InteractWorldItem):
    item_definition = ItemDefinition(
        item_id='radna',
        description='Radna',
        pickup_text='Radna',
        title = 'Radna',
        pickup_ui_image_path='assets/sprites/ui/overlay/items/placeholder/placeholder.png',
    )
    inventory_level = 1
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.level = type(self).inventory_level#the level of ring reuried to equip

    def pickup(self, player):
        self.mark_picked_up()        
        copy_item = RadnaEntry.from_item_class(type(self), self.game_objects)
        player.backpack.radna.add(copy_item)
        self.game_objects.signals.emit('item_interacted', item = self, player = player)
        self.kill()

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
        cls.pool_interactable_sprite(game_objects)
        cls.pool_pickup_ui_images(game_objects)
