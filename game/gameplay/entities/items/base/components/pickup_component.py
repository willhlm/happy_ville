class PickupComponent:
    supports_magnet = False

    def on_collision(self, item, entity):
        pass

    def interact(self, item, player):
        pass


class CollisionPickupComponent(PickupComponent):
    supports_magnet = True

    def on_collision(self, item, entity):
        if entity != item.game_objects.player:
            return
        item.pickup(entity)

    def collect_to_inventory(self, item, player):
        if hasattr(item, 'sounds'):
            item.game_objects.sound.play_sfx(item.sounds['death'][0], vol=0.3)
        player.backpack.inventory.add_item(item.get_item_id())
        item.currentstate.handle_input('death')


class InteractionPickupComponent(PickupComponent):
    def interact(self, item, player):
        item.pickup(player)
