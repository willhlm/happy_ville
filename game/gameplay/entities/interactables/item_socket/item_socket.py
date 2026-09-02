"""A persistent socket that trades an inventory item for a world change."""

import pygame

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables


class ItemSocket(Interactables):
    """Consume (or install) one item, then emit an authored signal."""

    WORLD_STATE_GROUP = "item_socket"

    def __init__(self, pos, game_objects, *, socket_id, item_id,
                 consume_item=True, signal_id=None,
                 signal_action="activate", signal_value=None,
                 sprite_path="assets/sprites/entities/interactables/item_sockets/gear_box/"):
        super().__init__(pos, game_objects)
        self.socket_id = str(socket_id)
        self.item_id = str(item_id)
        self.consume_item = bool(consume_item)
        self.signal_id = str(signal_id) if signal_id else None
        self.signal_action = str(signal_action)
        self.signal_value = signal_value
        if not self.signal_id:
            raise ValueError("An item socket needs signal_id.")

        self.sprites = read_files.load_sprites_dict(sprite_path, game_objects)
        self.image = self.sprites["idle"][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.installed = game_objects.world_state.objects.load_bool(
            game_objects.map.biome_room_name, self.WORLD_STATE_GROUP,
            self.socket_id, initial=False,
        )

    def interact(self, player=None):
        if self.installed:
            return False
        player = player or self.game_objects.player
        inventory = player.backpack.inventory
        if inventory.get_quantity(self.item_id) <= 0:
            return False

        self._emit_activation()
        if self.consume_item:
            inventory.remove(self.item_id)
        self.installed = self.game_objects.world_state.objects.set_bool(
            self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP,
            self.socket_id, True,
        )
        return True

    def _emit_activation(self):
        self.game_objects.signals.emit(
            self.signal_id,
            action=self.signal_action,
            value=self.signal_value,
            socket=self,
        )
