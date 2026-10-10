"""Composition root for Golden Fields-specific world systems."""

from .water_relay_controller import WaterRelayController
from .windmill_controller import WindmillController


class GoldenFieldsController:
    """Own the Golden Fields source providers and their puzzle state."""

    def __init__(self, game_objects, world_controller, power_controller):
        self.windmills = WindmillController(
            game_objects,
            world_controller,
            power_controller,
        )
        self.water_relays = WaterRelayController(
            game_objects,
            world_controller,
            power_controller,
            self.windmills,
        )
        world_controller.register_region_controller(self)

    def refresh(self):
        return self.windmills.refresh()
