import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states

class CallBell(Interactables):
    """A hit-operated bell emitting a generic signal once per ring.

    Tiled properties: signal_id, action (default activate), and value.
    For a lift, use its signal_id, action=request_station, and value=station.
    """
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/call_bell/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.signal_id = kwarg.get('signal_id', kwarg.get('ID', None))# ``ID`` is retained only as the legacy Tiled spelling of ``signal_id``.
        self.action = kwarg.get('action', 'activate')
        self.value = kwarg.get('value')
        self.currentstate = states.Idle(self)

    def take_dmg(self, effect):
        self.currentstate.handle_input('Ring')
        return effect

    def emit_signal(self):
        if self.signal_id:
            self.game_objects.signals.emit(
                self.signal_id,
                action=self.action,
                value=self.value,
                switch=self,
            )
