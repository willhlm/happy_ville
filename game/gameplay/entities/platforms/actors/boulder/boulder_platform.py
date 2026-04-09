from gameplay.entities.platforms.base.stateful_textured_platform import StatefulTexturedPlatform
from engine.utils import read_files

class BoulderPlatform(StatefulTexturedPlatform):
    def __init__(self, pos, game_objects):
        initial_state = "down" if game_objects.world_state.narrative.events.get("reindeer", False) else "erect"
        super().__init__(pos, game_objects, initial_state=initial_state)

    def load_sprites(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/boulder/', self.game_objects)
        return self.sprites
