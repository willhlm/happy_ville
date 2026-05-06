from engine.utils import functions

from gameplay.entities.interactables import Grind, InteractableCocoon, InteractableVines, StoneWood
from gameplay.entities.visuals.environments import BackgroundCocoon, GeneralTree

from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.nordveden import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Nordveden(Biome):
    default_room_config = DEFAULT_ROOM_CONFIG
    room_configs = ROOM_CONFIGS

    def post_process(self, layer_name, parallax):
        if self.live_blur:
            if parallax[0] == 1: return
            radius = functions.blur_radius(parallax)
            self.level.game_objects.game.screen_manager.append_shader("Blur_fast", [layer_name], radius=radius)

    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])

            source, firstgid, local_id = resolve_tileset(map_def, obj["gid"])
            if "objects" not in source:
                continue
            id = local_id

            if id == 2:
                name = "nordveden/tree_1/"
                new_tree = GeneralTree(object_position, self.level.game_objects, parallax, layer_name, name)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_tree)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_tree)

            elif id == 3:
                name = "nordveden/tree_2/"
                new_tree = GeneralTree(object_position, self.level.game_objects, parallax, layer_name, name)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_tree)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_tree)

            elif id == 5:
                kwarg = {}
                for property in properties:
                    if property["name"] == "frequency":
                        kwarg["frequency"] = property["value"]
                    elif property["name"] == "direction":
                        kwarg["direction"] = property["value"]
                    elif property["name"] == "distance":
                        kwarg["distance"] = property["value"]
                    elif property["name"] == "speed":
                        kwarg["speed"] = property["value"]

                new_grind = Grind(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_grind)

            elif id == 6:
                kwarg = {}
                for property in properties:
                    if property["name"] == "quest":
                        kwarg["quest"] = property["value"]
                    elif property["name"] == "item":
                        kwarg["item"] = property["value"]

                new_stone_wood = StoneWood(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_stone_wood)

            elif id == 7:
                if parallax == [1, 1]:
                    new_cocoon = InteractableCocoon(object_position, self.level.game_objects)
                    self.level.game_objects.interactables.add(new_cocoon)
                else:
                    new_cocoon = BackgroundCocoon(object_position, self.level.game_objects, parallax)
                    if layer_name.startswith("fg"):
                        self.level.game_objects.all_fgs.add(layer_name, new_cocoon)
                    else:
                        self.level.game_objects.all_bgs.add(layer_name, new_cocoon)

            elif id == 8:
                new_boss = self.level.game_objects.registry.fetch("enemies", "cocoon_boss")(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(new_boss)

            elif id == 9:
                sprite_path = 'nordveden/vines_1/'
                new_vine = InteractableVines(object_position, self.level.game_objects, path = sprite_path)
                self.level.game_objects.interactables_fg.add(new_vine)
