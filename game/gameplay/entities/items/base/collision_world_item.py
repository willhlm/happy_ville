from .world_item import WorldItem


class CollisionWorldItem(WorldItem):
    supports_magnet = True
    magnet_delay = 0

    def on_collision(self, entity):
        if entity != self.game_objects.player:
            return False
        return self.try_pickup(entity)

    def interact(self, player):
        return False

    def add_to_inventory(self, player, item_id=None):
        if item_id is None:
            item_id = self.get_item_id()
        player.backpack.inventory.add_item(item_id)