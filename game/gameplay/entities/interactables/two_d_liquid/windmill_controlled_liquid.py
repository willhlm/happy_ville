from .two_d_liquid import TwoDLiquid

'''
height: 20
height_per_active: 25
windmill_level: golden_fields_1
windmill_ids: windmill_1,windmill_2,windmill_3
'''

class WindmillControlledLiquid(TwoDLiquid):
    """A liquid whose initial level rises for each active linked windmill."""

    WINDMILL_STATE_GROUP = "windmill"

    def __init__(self, pos, game_objects, size, layer_name, **properties):
        self.windmill_ids = self._parse_ids(properties.get("windmill_ids", ""))
        self.windmill_level = properties.get("windmill_level") or game_objects.map.biome_room_name
        self.base_height_percent = float(properties.get("height", 100.0))
        self.height_per_active = float(properties.get("height_per_active", 0.0))

        super().__init__(pos, game_objects, size, layer_name, **properties)
        self.set_height_percent(
            self.base_height_percent + self.active_windmill_count() * self.height_per_active
        )

    @staticmethod
    def _parse_ids(value):
        return tuple(part.strip() for part in str(value).split(",") if part.strip())

    def active_windmill_count(self):
        objects = self.game_objects.world_state.objects
        return sum(
            objects.peek_value(
                self.windmill_level,
                self.WINDMILL_STATE_GROUP,
                windmill_id,
                default="idle",
            ) == "active"
            for windmill_id in self.windmill_ids
        )
