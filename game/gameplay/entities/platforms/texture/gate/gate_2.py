from engine.utils import read_files
from .gate_1 import Gate_1

class Gate_2(Gate_1):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

    def init(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/gates/gate_2/', self.game_objects)
