from gameplay.entities.interactables import DropletSource
from gameplay.entities.platforms import BridgePlatform

from ..helpers import calculate_object_position, resolve_tileset
from .base import Biome
from .configs.golden_fields import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Golden_fields(Biome):
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

            if id == 2:
                new_bridge = BridgePlatform(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_bridge)

            elif id == 3:
                if layer_name.startswith("fg"):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs

                new_drop = DropletSource(object_position, self.level.game_objects, parallax, layer_name, group)
                group.add(layer_name, new_drop)
