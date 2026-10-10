"""Liquid whose initial level is controlled by a named power source."""

from .two_d_liquid import TwoDLiquid


class WaterRelayControlledLiquid(TwoDLiquid):
    """Choose its liquid level from power state when the map is loaded."""

    def __init__(self, pos, game_objects, size, layer_name, **properties):
        self.power_source = str(properties["power_source"]).strip()
        self.relay_angle = int(properties.get("relay_angle", 0)) % 360

        self.inactive_height_percent = float(properties.get("height", 0.0))
        self.active_height_percent = float(properties.get("relay_height", 100.0))
        properties["height"] = self.inactive_height_percent
        super().__init__(pos, game_objects, size, layer_name, **properties)

        powered = self.game_objects.world_controller.power.is_powered(
            self.power_source,
            relay_angle=self.relay_angle,
        )
        self.set_height_percent(
            self.active_height_percent
            if powered
            else self.inactive_height_percent
        )
