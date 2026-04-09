from engine.utils import read_files
from .locked_door_platform import LockedDoorPlatform

class RightDoorPlatform(LockedDoorPlatform):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)        
        self.hitbox[2] = self.hitbox[2] - 8
        self.hitbox.bottomright = self.rect.bottomright

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/doors/door_right/', self.game_objects)
        return self.sprites
