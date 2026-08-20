from .two_d_liquid import TwoDLiquid

'''
height: 20
height_per_active: 25
wind_network: golden_fields_liquid
'''

class WindmillControlledLiquid(TwoDLiquid):
    """A liquid that reflects the state of a registered windmill network."""

    def __init__(self, pos, game_objects, size, layer_name, **properties):
        self.base_height_percent = float(properties.get("height", 100.0))
        self.height_per_active = float(properties.get("height_per_active", 0.0))
        self.wind_network = str(properties["wind_network"])

        super().__init__(pos, game_objects, size, layer_name, **properties)
        controller = self.game_objects.world_controller.golden_fields
        self.apply_windmill_count(controller.windmill_turning_count(self.wind_network))
        controller.subscribe_windmill_network(self.wind_network, self._on_network_changed)

    def _on_network_changed(self, *, turning_count, **kwargs):
        self.apply_windmill_count(turning_count)

    def apply_windmill_count(self, turning_count):
        self.set_height_percent(self.base_height_percent + turning_count * self.height_per_active)

    def release_texture(self):
        self.game_objects.world_controller.golden_fields.unsubscribe_windmill_network(
            self.wind_network, self._on_network_changed
        )
        super().release_texture()
