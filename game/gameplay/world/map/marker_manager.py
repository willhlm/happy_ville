class MapMarkerManager:
    """Unlock map markers and translate room-local positions into map coordinates."""

    def __init__(self, game_objects):
        self.game_objects = game_objects

    def unlock(
        self,
        marker_id,
        room_position,
        *,
        room_id=None,
        map_name=None,
        **metadata,
    ):
        map_definition = self.game_objects.map.map_def
        if map_definition is not None:
            room_id = room_id or map_definition.biome_room_name
            map_name = map_name or map_definition.biome_name

        if room_id is None:
            return None

        map_name = map_name or room_id.rpartition('_')[0] or room_id
        normalized_position = self.normalize_room_position(
            room_position,
            map_definition,
        )
        return self.game_objects.world_state.map_state.unlock_marker(
            map_name,
            marker_id,
            room_id=room_id,
            normalized_room_position=normalized_position,
            **metadata,
        )

    @staticmethod
    def normalize_room_position(room_position, map_definition):
        if map_definition is None or room_position is None:
            return None

        room_data = map_definition.map_data
        room_width = room_data.get('width', 0) * room_data.get('tilewidth', 0)
        room_height = room_data.get('height', 0) * room_data.get('tileheight', 0)
        if room_width <= 0 or room_height <= 0:
            return None

        return [
            max(0.0, min(1.0, room_position[0] / room_width)),
            max(0.0, min(1.0, room_position[1] / room_height)),
        ]
