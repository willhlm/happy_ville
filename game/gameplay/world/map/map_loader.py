from typing import Dict

import pygame

from engine import constants as C
from engine.utils import read_files

from .map_data import MapDefinition


class WorldResetter:
    """
    Owns: group/screen/shader/light resets for a new map.
    """

    def __init__(self, game_objects):
        self.game_objects = game_objects

    def reset_for_new_map(self):
        self.game_objects.sound.clear_spatial_sounds()
        self.game_objects.clean_groups()
        self.game_objects.game.screen_manager.clear_screens()
        self.game_objects.player.shader_state.handle_input("idle")
        self.game_objects.lights.new_map()


class MapDataLoader:
    """
    Owns: reading JSON + format_tiled_json_group + resolving firstgid.
    Underlying map_data is unchanged.
    """

    def __init__(self):
        self.tile_size = C.tile_size

    def load(self, biome_room_name: str) -> MapDefinition:
        biome_name = biome_room_name[: biome_room_name.rfind("_")]
        raw = read_files.read_json(f"assets/maps/{biome_name}/{biome_room_name}.json")
        map_data = read_files.format_tiled_json_group(raw)

        statics_firstgid = 0
        interactables_firstgid = 0
        objects_firstgid = 0
        platforms_firstgid = 0

        for tileset in map_data.get("tilesets", []):
            source = tileset.get("source")
            if not source:
                continue
            if "static" in source:
                statics_firstgid = tileset["firstgid"]
            elif "interactables" in source:
                interactables_firstgid = tileset["firstgid"]
            elif "objects" in source:
                objects_firstgid = tileset["firstgid"]
            elif "platforms" in source:
                platforms_firstgid = tileset["firstgid"]

        map_data["statics_firstgid"] = statics_firstgid
        map_data["interactables_firstgid"] = interactables_firstgid
        map_data["objects_firstgid"] = objects_firstgid
        map_data["platforms_firstgid"] = platforms_firstgid

        tileset_ranges = []
        for tileset in map_data.get("tilesets", []):
            source = tileset.get("source")
            if source:
                tileset_ranges.append((tileset["firstgid"], source))
        tileset_ranges.sort(key=lambda x: x[0])

        return MapDefinition(
            biome_room_name=biome_room_name,
            biome_name=biome_name,
            map_data=map_data,
            statics_firstgid=statics_firstgid,
            interactables_firstgid=interactables_firstgid,
            objects_firstgid=objects_firstgid,
            platforms_firstgid=platforms_firstgid,
            tileset_ranges=tileset_ranges,
        )

    def read_all_spritesheets(self, biome_room_name: str, map_data: dict) -> Dict[int, pygame.Surface]:
        sprites: Dict[int, pygame.Surface] = {}
        biome_name = biome_room_name[: biome_room_name.rfind("_")]

        for tileset in map_data.get("tilesets", []):
            if "source" in tileset:
                continue

            sheet = pygame.image.load(f"assets/maps/{biome_name}/{tileset['image']}").convert_alpha()

            rows = int(sheet.get_rect().h / self.tile_size)
            columns = int(sheet.get_rect().w / self.tile_size)
            n = tileset["firstgid"]

            for row in range(rows):
                for col in range(columns):
                    y = row * self.tile_size
                    x = col * self.tile_size
                    rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    img = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA, 32).convert_alpha()
                    img.blit(sheet, (0, 0), rect)
                    sprites[n] = img
                    n += 1

        return sprites
