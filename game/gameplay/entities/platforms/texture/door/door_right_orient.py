from engine.utils import read_files
from .door import Door

class DoorRightOrient(Door):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)        
        self.hitbox[2] = self.hitbox[2] - 8
        self.hitbox.bottomright = self.rect.bottomright

    def init(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/door_right/', self.game_objects)
