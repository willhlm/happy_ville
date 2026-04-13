from ..helpers import calculate_object_position, resolve_tileset
from ..room_config import RoomConfig, merge_room_configs
from .base import Biome
from .configs.rhoutta_encounter import DEFAULT_ROOM_CONFIG, ROOM_CONFIGS


class Rhoutta_encounter(Biome):
    default_room_config = DEFAULT_ROOM_CONFIG
    room_configs = ROOM_CONFIGS

    def get_room_config(self, room_id: str) -> RoomConfig:
        config = super().get_room_config(room_id)
        if room_id == "2" and self.level.game_objects.world_state.narrative.events.get("guide", False):
            config = merge_room_configs(
                config,
                RoomConfig(player_lights=[{"colour": [200 / 255, 200 / 255, 200 / 255, 200 / 255], "interact": False}]),
            )
        return config

    def load_objects(self, data, parallax, offset, ctx, map_def, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = calculate_object_position(obj, parallax, offset, viewport_center)
            source, firstgid, local_id = resolve_tileset(map_def, obj["gid"])
            if "objects" not in source:
                continue
