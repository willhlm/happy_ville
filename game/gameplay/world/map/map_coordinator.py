# map_coordinator.py

from time import perf_counter
from typing import Optional

from .utils import WorldResetter, MapDataLoader, BiomeManager, SceneBuilder, LoadContext
from .map_data import MapDefinition  # make sure this import is correct in your project

class MapCoordinator:
    """
    Owns: reset + load pipeline orchestration.
    Does NOT own: fade / transition choreography.
    """
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.level_name: str = ""

        self.resetter = WorldResetter(game_objects)

        self.data_loader = MapDataLoader()
        self.game_objects.map_loader_data = self.data_loader  # keep your existing integration

        self.biome_mgr = BiomeManager(self)
        self.scene_builder = SceneBuilder(game_objects)

        self.ctx: Optional[LoadContext] = None
        self.map_def: Optional[MapDefinition] = None

    def load_map(self, previous_state, map_name: str, spawn="1", fade=True):
        map_name = map_name.lower()
        self.game_objects.transition.run(previous_state, style = "fade_black", action = lambda: self.load_now(map_name, spawn))

    def load_now(self, map_name: str, spawn="1"):
        """Call this ONLY when screen is already black."""
        map_name = map_name.lower()
        self.level_name = map_name
        self._do_load(map_name, spawn)

    # ---- internal pipeline ----
    def _do_load(self, map_name: str, spawn):
        self.resetter.reset_for_new_map()

        t0 = perf_counter()
        self.ctx = LoadContext(level_name=map_name, spawn=spawn)

        self.biome_mgr.update_for_level(map_name)

        self.map_def = self.data_loader.load(map_name)

        self.scene_builder.build(self.map_def, self.ctx, self.biome_mgr)

        self.biome_mgr.set_camera(self.ctx)

        self._organise_references()

        print(perf_counter() - t0)

    def _organise_references(self):
        for i, bg_fade in enumerate(self.ctx.references['bg_fade']):
            for j in range(i + 1, len(self.ctx.references['bg_fade'])):
                if bg_fade.hitbox.colliderect(self.ctx.references['bg_fade'][j].hitbox):
                    bg_fade.add_child(self.ctx.references['bg_fade'][j])
                    self.ctx.references['bg_fade'][j].add_child(bg_fade)
