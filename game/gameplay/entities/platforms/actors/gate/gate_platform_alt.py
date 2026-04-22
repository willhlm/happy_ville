from engine.utils import read_files
from .gate_platform import GatePlatform

class GatePlatformAlt(GatePlatform):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/gates/gate_2/', self.game_objects)
        return self.sprites
