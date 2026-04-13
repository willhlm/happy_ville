import math
from typing import TYPE_CHECKING

import pygame

from engine import constants as C
from engine import groups
from engine.utils import read_files

from gameplay.entities.visuals.environments import BgAnimated, BgBlock, BgFade

from .helpers import props_list_to_dict
from .map_data import LoadContext, MapDefinition
from .spawners import ObjectSpawner

if TYPE_CHECKING:
    from .biome_manager import BiomeManager


class SceneBuilder:
    """
    Owns: turning MapDefinition + sprites into groups/layers/objects in the world.
    Delegates entity creation to ObjectSpawner.
    """

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.tile_size = C.tile_size
        self.TILE_SIZE = C.tile_size
        self.spawner = ObjectSpawner(game_objects)

    def ensure_state_file(self, biome_room_name: str):
        if not self.game_objects.world_state.objects.has_level(biome_room_name):
            self.game_objects.world_state.objects.init_level(biome_room_name)

    def build(self, map_def: MapDefinition, ctx: LoadContext, biome_mgr: "BiomeManager"):
        map_data = map_def.map_data
        viewport_center = self.game_objects.game.viewport_center

        self.ensure_state_file(map_def.biome_room_name)
        ctx.spritesheet_dict = self.game_objects.map_loader_data.read_all_spritesheets(map_def.biome_room_name, map_data)

        for group in map_data["groups"]:
            gdata = map_data["groups"][group]
            parallax = [gdata["parallaxx"], gdata["parallaxy"]]
            offset = [gdata["offsetx"], gdata["offsety"]]

            self.game_objects.game.screen_manager.register_screen(group, parallax)

            if group.startswith("bg"):
                self.game_objects.all_bgs.new_group(group, groups.LayeredUpdates())
            else:
                self.game_objects.all_fgs.new_group(group, groups.LayeredUpdates())

            self._load_objects(gdata["objects"], parallax, offset, "back", ctx, biome_mgr, map_def, group, viewport_center)
            self._load_layers(gdata["layers"], parallax, offset, ctx, map_def, group, biome_mgr.biome, viewport_center)
            self._load_objects(gdata["objects"], parallax, offset, "front", ctx, biome_mgr, map_def, group, viewport_center)

            biome_mgr.configure_weather(group, parallax)
            biome_mgr.post_process(group, parallax)

    def _load_objects(self, data, parallax, offset, position: str, ctx: LoadContext, biome_mgr: "BiomeManager", map_def: MapDefinition, layer_name: str, viewport_center):
        if position == "back":
            if "back" in data:
                biome_mgr.load_biome_objects(data["back"], parallax, offset, ctx=ctx, map_def=map_def, layer_name=layer_name, viewport_center=viewport_center)
            return

        if "paths" in data:
            self.spawner.load_paths(data["paths"], parallax, offset, ctx=ctx, viewport_center=viewport_center)

        if "statics" in data:
            self.spawner.load_statics(data["statics"], parallax, offset, ctx=ctx, map_def=map_def, layer_name=layer_name, viewport_center=viewport_center)

        if "interactables" in data:
            self.spawner.load_interactables(data["interactables"], parallax, offset, map_def=map_def, layer_name=layer_name, viewport_center=viewport_center)

        if "platforms" in data:
            self.spawner.load_platforms(data["platforms"], parallax, offset, ctx=ctx, layer_name=layer_name, viewport_center=viewport_center)

        if "front" in data:
            biome_mgr.load_biome_objects(data["front"], parallax, offset, ctx=ctx, map_def=map_def, layer_name=layer_name, viewport_center=viewport_center)

    def _load_layers(self, data, parallax, offset, ctx: LoadContext, map_def: MapDefinition, layer_name: str, biome, viewport_center):
        key = list(data.keys())[0]
        cols = data[key]["width"]
        rows = data[key]["height"]

        blit_surfaces = {}
        blit_compress_surfaces = {}
        animation_list = {}
        blit_fade_surfaces = {}
        blit_fade_pos = {}

        for tile_layer in data.keys():
            animation_list[tile_layer] = []
            if "animated" in tile_layer:
                continue
            blit_surfaces[tile_layer] = pygame.Surface((cols * self.tile_size, rows * self.tile_size), pygame.SRCALPHA, 32)
            blit_compress_surfaces[tile_layer[0 : tile_layer.rfind("_")]] = pygame.Surface((cols * self.tile_size, rows * self.tile_size), pygame.SRCALPHA, 32)
            blit_fade_surfaces[tile_layer] = pygame.Surface((cols * self.tile_size, rows * self.tile_size), pygame.SRCALPHA, 32)
            blit_fade_pos[tile_layer] = []

        new_map_diff = [-viewport_center[0], -viewport_center[1]]
        for tile_layer in data.keys():
            for index, tile_number in enumerate(data[tile_layer]["data"]):
                if tile_number == 0:
                    continue
                y = math.floor(index / cols)
                x = index - (y * cols)

                if "animated" in tile_layer:
                    for tileset in map_def.map_data["tilesets"]:
                        if tile_number == tileset["firstgid"]:
                            biome_name = map_def.biome_name
                            path = "maps/%s/%s" % (biome_name, read_files.get_folder(tileset["image"]))
                            blit_pos = (
                                x * self.tile_size - math.ceil(new_map_diff[0] * (1 - parallax[0])) + offset[0] + data[tile_layer]["offsetx"],
                                y * self.TILE_SIZE - math.ceil((1 - parallax[1]) * new_map_diff[1]) + offset[1] + data[tile_layer]["offsety"],
                            )
                            animation_list[tile_layer].append(BgAnimated(self.game_objects, blit_pos, path, parallax))
                else:
                    blit_pos = (x * self.tile_size + data[tile_layer]["offsetx"], y * self.tile_size + data[tile_layer]["offsety"])
                    blit_surfaces[tile_layer].blit(ctx.spritesheet_dict[tile_number], blit_pos)
                    blit_fade_pos[tile_layer].append(blit_pos)

        animation_entities = {}
        for layer in data.keys():
            bg = layer[0 : layer.rfind("_")]
            if "animated" in layer:
                animation_entities.setdefault(bg, []).append(animation_list[layer])
            elif "fade" in layer:
                blit_fade_surfaces[layer].blit(blit_surfaces[layer], (0, 0))
            else:
                blit_compress_surfaces[bg].blit(blit_surfaces[layer], (0, 0))

        for tile_layer in blit_compress_surfaces.keys():
            pos = (-math.ceil((1 - parallax[0]) * new_map_diff[0]) + offset[0], -math.ceil((1 - parallax[1]) * new_map_diff[1]) + offset[1])

            if "fade" in tile_layer:
                for fade in blit_fade_surfaces.keys():
                    if "fade" in fade:
                        layer_props = props_list_to_dict(data[fade].get("properties", []))
                        bg = BgFade(pos, self.game_objects, blit_fade_surfaces[fade], parallax, blit_fade_pos[fade], data[fade]["id"], **layer_props)
                        if layer_name.startswith("bg"):
                            self.game_objects.all_bgs.add(layer_name, bg)
                        else:
                            self.game_objects.all_fgs.add(layer_name, bg)

                        self.game_objects.bg_fade.add(bg)
                        ctx.references["bg_fade"].append(bg)

            elif "interact" in tile_layer:
                self.game_objects.bg_interact.add(BgBlock(pos, self.game_objects, blit_compress_surfaces[tile_layer], parallax, live_blur=biome.live_blur))

            elif layer_name.startswith("bg"):
                bg = BgBlock(pos, self.game_objects, blit_compress_surfaces[tile_layer], parallax, live_blur=biome.live_blur)
                self.game_objects.all_bgs.add(layer_name, bg)
            elif layer_name.startswith("fg"):
                self.game_objects.all_fgs.add(layer_name, BgBlock(pos, self.game_objects, blit_compress_surfaces[tile_layer], parallax, live_blur=biome.live_blur))

            if animation_entities.get(tile_layer, False):
                for bg_animation in animation_entities[tile_layer]:
                    if "fg" in tile_layer:
                        self.game_objects.all_fgs.add(layer_name, bg_animation)
                    elif "bg" in tile_layer:
                        self.game_objects.all_bgs.add(layer_name, bg_animation)
