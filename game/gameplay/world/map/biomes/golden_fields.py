from gameplay.entities.interactables import DropletSource
from gameplay.entities.platforms import BridgePlatform

from ..helpers import calculate_object_position, props_list_to_dict, resolve_tileset
from .base import Biome
from .configs.golden_fields import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS
from gameplay.entities.visuals.environments import Windmill


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

            if id == 4:
                kwargs = props_list_to_dict(properties)
                new_mill = Windmill(
                    object_position,
                    self.level.game_objects,
                    parallax,
                    layer_name,
                    kwargs.get("id"),
                    initial_state=kwargs.get("initial_state", "idle"),
                )
                if layer_name.startswith("fg"):
                    self.level.game_objects.all_fgs.add(layer_name, new_mill)
                else:
                    self.level.game_objects.all_bgs.add(layer_name, new_mill)
