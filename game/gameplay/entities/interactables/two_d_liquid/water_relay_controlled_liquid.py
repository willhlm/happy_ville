"""Liquid whose level is controlled by a WaterRelayController outlet."""

from .two_d_liquid import TwoDLiquid
from gameplay.world.configs.golden_fields_systems import WATER_RELAY_ANGLES


class WaterRelayControlledLiquid(TwoDLiquid):
    """Fill only while its relay is enabled, flowing, and correctly aimed."""

    def __init__(self, pos, game_objects, size, layer_name, **properties):
        self.relay_id = str(properties["relay_id"])
        self.relay_angle = int(properties.get("relay_angle", 0)) % 360
        if self.relay_angle not in WATER_RELAY_ANGLES:
            valid_angles = ", ".join(str(value) for value in WATER_RELAY_ANGLES)
            raise ValueError(f"relay_angle must be one of: {valid_angles}.")

        self.inactive_height_percent = float(properties.get("height", 0.0))
        self.active_height_percent = float(properties.get("relay_height", 100.0))
        properties["height"] = self.inactive_height_percent
        super().__init__(pos, game_objects, size, layer_name, **properties)

        controller = self.game_objects.world_controller.water_relays
        self.apply_relay_state(controller.get_state(self.relay_id))
        controller.subscribe(self.relay_id, self._on_relay_changed)

    def _on_relay_changed(self, **state):
        self.apply_relay_state(state)

    def apply_relay_state(self, state):
        is_supplied = (
            state["enabled"]
            and state["flowing"]
            and state["angle"] == self.relay_angle
        )
        self.set_height_percent(
            self.active_height_percent if is_supplied else self.inactive_height_percent
        )

    def release_texture(self):
        self.game_objects.world_controller.water_relays.unsubscribe(
            self.relay_id, self._on_relay_changed
        )
        super().release_texture()
