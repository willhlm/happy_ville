import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_lever
from engine import constants as C

class Lever(Interactables):
    """A hit-operated lever that emits a ``signal_id``, ``action``, ``value`` event."""
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/lever/', game_objects)
        self.image = self.sprites['off'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.signal_id = kwarg.get('signal_id', kwarg.get('ID', None))# ``ID`` is retained only as the legacy Tiled spelling of ``signal_id``.
        self.action = kwarg.get('action', 'toggle')
        self.value = kwarg.get('value')

        on = self.game_objects.world_state.objects.load_bool(self.game_objects.map.biome_room_name, "lever", self.signal_id, initial=kwarg.get("on", False))
        self.currentstate = states_lever.On(self) if on else states_lever.Off(self)     

    def take_dmg(self, effect):
        self.currentstate.handle_input("Transform")
        self.game_objects.world_state.objects.toggle_bool(self.game_objects.map.biome_room_name, "lever", self.signal_id)
        self.game_objects.signals.emit(
            self.signal_id,
            action=self.action,
            value=self.value,
            switch=self,
        )
        return effect
