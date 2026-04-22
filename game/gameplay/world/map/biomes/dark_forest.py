from gameplay.entities.interactables import ShadowLightLantern
from gameplay.entities.platforms.shadow_light.dark_forest_1 import DarkForest_1
from gameplay.entities.visuals.environments import SmallTree_1, Vines_1

from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.dark_forest import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Dark_forest(Biome):
    default_room_config = DEFAULT_ROOM_CONFIG
    room_configs = ROOM_CONFIGS

    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])
            source, firstgid, local_id = resolve_tileset(map_def, obj["gid"])
            if "objects" not in source:
                continue
            id = local_id

            if id == 9:
                new_viens = Vines_1(object_position, self.level.game_objects, parallax)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_viens)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_viens)

            elif id == 10:
                new_viens = SmallTree_1(object_position, self.level.game_objects, parallax)
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_viens)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_viens)

            elif id == 11:
                new_block = DarkForest_1(object_position, self.level.game_objects)
                self.level.game_objects.cosmetics.add(new_block)

            elif id == 12:
                kwarg = {}
                for property in properties:
                    if property["name"] == "on":
                        kwarg["on"] = property["value"]
                new_lantern = ShadowLightLantern(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_lantern)
