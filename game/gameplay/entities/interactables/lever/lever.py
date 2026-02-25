import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_lever
from engine import constants as C

class Lever(Interactables):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/lever/', game_objects)
        self.image = self.sprites['off'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.ID_key = kwarg.get('ID', None)#an ID to match with the reference (gate or platform etc) and an unique ID key to identify which item that the player is intracting within the world

        on = self.game_objects.world_state.load_bool(self.game_objects.map.level_name, "lever", self.ID_key, initial=kwarg.get("on", False))
        self.currentstate = states_lever.On(self) if on else states_lever.Off(self)     

    def take_dmg(self, effect):
        self.currentstate.handle_input("Transform")
        self.game_objects.world_state.toggle_bool(self.game_objects.map.level_name, "lever", self.ID_key)
        self.game_objects.signals.emit(self.ID_key)
        return effect
