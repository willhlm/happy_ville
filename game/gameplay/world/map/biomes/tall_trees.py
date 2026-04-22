from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.tall_trees import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Tall_trees(Biome):
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

            if id == 10:
                kwarg = {}
                for property in properties:
                    if property["name"] == "direction":
                        kwarg["direction"] = property["value"]

                new_enemy = self.level.game_objects.registry.fetch("enemies", "packun")(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.enemies.add(new_enemy)
