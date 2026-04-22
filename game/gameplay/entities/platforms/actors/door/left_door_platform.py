from engine.utils import read_files
from .locked_door_platform import LockedDoorPlatform

class LeftDoorPlatform(LockedDoorPlatform):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)        

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/doors/door_left/', self.game_objects)
        return self.sprites
