from engine.utils import read_files
from .door import Door

class DoorLeftOrient(Door):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)        

    def init(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/doors/door_left/', self.game_objects)
