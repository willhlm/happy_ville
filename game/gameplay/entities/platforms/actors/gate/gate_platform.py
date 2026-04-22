from gameplay.entities.platforms.base.stateful_textured_platform import WorldStateDrivenPlatform
from engine.utils import read_files

class GatePlatform(WorldStateDrivenPlatform):
    world_state_group = "gate"

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/platforms/gates/gate_1/", self.game_objects)
        return self.sprites
