# map_coordinator.py

from time import perf_counter
from typing import Optional

from .biome_manager import BiomeManager
from .map_data import LoadContext, MapDefinition
from .map_loader import MapDataLoader, WorldResetter
from .scene_builder import SceneBuilder

class MapCoordinator:
    """
    Owns: reset + load pipeline orchestration.
    Does NOT own: fade / transition choreography.
    """
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.biome_room_name: str = ""

        self.resetter = WorldResetter(game_objects)

        self.data_loader = MapDataLoader()
        self.game_objects.map_loader_data = self.data_loader  # keep your existing integration

        self.biome_mgr = BiomeManager(self)
        self.scene_builder = SceneBuilder(game_objects)

        self.ctx: Optional[LoadContext] = None
        self.map_def: Optional[MapDefinition] = None

    def load_map(self, previous_state, biome_room_name: str, spawn="1", fade=True):
        biome_room_name = biome_room_name.lower()
        self.game_objects.transition.run(previous_state, style = "fade_black", action = lambda: self.load_now(biome_room_name, spawn))

    def load_now(self, biome_room_name: str, spawn="1"):
        """Call this ONLY when screen is already black."""
        biome_room_name = biome_room_name.lower()
        self.biome_room_name = biome_room_name
        self._do_load(biome_room_name, spawn)

    # ---- internal pipeline ----
    def _do_load(self, biome_room_name: str, spawn):
        self.resetter.reset_for_new_map()

        t0 = perf_counter()
        self.ctx = LoadContext(biome_room_name=biome_room_name, spawn=spawn)

        self.biome_mgr.update_for_biome_room(biome_room_name)

        self.map_def = self.data_loader.load(biome_room_name)
        self.game_objects.world_state.map_state.visit_area(self.map_def.biome_name, self.map_def.biome_room_name)

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
