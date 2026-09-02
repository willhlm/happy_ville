"""Golden Fields-specific derived world state."""

from gameplay.world.configs.golden_fields_systems import (
    PISTON_PROFILES,
    WINDMILL_NETWORKS,
)


class GoldenFieldsController:
    """Own Golden Fields windmill networks, not global wind itself."""

    SIGNAL_PREFIX = "golden_fields:wind_network:"
    WINDMILL_ACTIVATION_SIGNAL = "golden_fields:activate_windmill"
    def __init__(self, game_objects, world_controller):
        self.game_objects = game_objects
        self.world_controller = world_controller
        self._networks = {}
        self._turning_counts = {}

        for network_id, config in WINDMILL_NETWORKS.items():
            self.register_windmill_network(network_id, **config)
        self.game_objects.signals.subscribe(
            self.WINDMILL_ACTIVATION_SIGNAL, self._on_windmill_activation
        )
        self.world_controller.subscribe(
            self.world_controller.WIND_AVAILABLE, self._on_global_wind_changed
        )
        self.world_controller.register_region_controller(self)

    @classmethod
    def signal_name(cls, network_id):
        return f"{cls.SIGNAL_PREFIX}{network_id}"

    def register_windmill_network(
        self,
        network_id,
        *,
        windmill_level,
        windmill_ids,
        windmill_initial_states=None,
    ):
        """Register a network and return its current turning-mill count."""
        windmill_ids = tuple(str(windmill_id) for windmill_id in windmill_ids)
        if not windmill_ids:
            raise ValueError("A windmill network needs at least one windmill ID.")

        initial_states = {
            str(windmill_id): state
            for windmill_id, state in (windmill_initial_states or {}).items()
        }
        unknown_ids = initial_states.keys() - set(windmill_ids)
        if unknown_ids:
            raise ValueError(
                f"Windmill defaults for unknown IDs: {', '.join(sorted(unknown_ids))}."
            )

        config = {
            "windmill_level": str(windmill_level),
            "windmill_ids": windmill_ids,
            "windmill_initial_states": initial_states,
        }
        if network_id in self._networks:
            if self._networks[network_id] != config:
                raise ValueError(
                    f"Windmill network '{network_id}' was registered with a different configuration."
                )
            return self.windmill_turning_count(network_id)

        self._networks[network_id] = config
        self._seed_windmill_states(config)
        self._turning_counts[network_id] = self._calculate_turning_count(config)
        return self._turning_counts[network_id]

    def windmill_turning_count(self, network_id):
        try:
            return self._turning_counts[network_id]
        except KeyError as error:
            raise KeyError(f"Unknown Golden Fields windmill network '{network_id}'.") from error

    def windmill_network_size(self, network_id):
        try:
            return len(self._networks[network_id]["windmill_ids"])
        except KeyError as error:
            raise KeyError(f"Unknown Golden Fields windmill network '{network_id}'.") from error

    def is_registered_windmill_network(self, network_id):
        return network_id in self._networks

    def activate_windmill(self, windmill_id):
        """Persistently activate an authored windmill by its network ID."""
        windmill_id = str(windmill_id)
        matches = [
            config for config in self._networks.values()
            if windmill_id in config["windmill_ids"]
        ]
        if len(matches) != 1:
            raise KeyError(f"Unknown or ambiguous Golden Fields windmill '{windmill_id}'.")
        config = matches[0]
        self.game_objects.world_state.objects.set_value(
            config["windmill_level"], "windmill", windmill_id, "active"
        )
        self.game_objects.signals.emit(windmill_id, state="active")
        self.refresh()

    def _on_windmill_activation(self, *, action, value, **kwargs):
        if action == "activate":
            self.activate_windmill(value)

    def piston_profile(self, profile_id, network_id, turning_count):
        """Return the authored piston profile for a network's turning count."""
        try:
            profiles = PISTON_PROFILES[profile_id]
        except KeyError as error:
            raise KeyError(f"Unknown Golden Fields piston profile '{profile_id}'.") from error

        if turning_count >= self.windmill_network_size(network_id) and "all" in profiles:
            return profiles["all"]

        count_profiles = [count for count in profiles if isinstance(count, int) and count <= turning_count]
        if not count_profiles:
            raise ValueError(f"Piston profile '{profile_id}' needs a profile for zero turning windmills.")
        return profiles[max(count_profiles)]

    def refresh(self):
        """Recalculate all networks after a mill or global-wind change."""
        return {
            network_id: self.refresh_windmill_network(network_id)
            for network_id in tuple(self._networks)
        }

    def refresh_windmill_network(self, network_id):
        try:
            config = self._networks[network_id]
        except KeyError as error:
            raise KeyError(f"Unknown Golden Fields windmill network '{network_id}'.") from error

        turning_count = self._calculate_turning_count(config)
        previous_count = self._turning_counts[network_id]
        self._turning_counts[network_id] = turning_count
        if turning_count != previous_count:
            self.game_objects.signals.emit(
                self.signal_name(network_id),
                network_id=network_id,
                turning_count=turning_count,
            )
        return turning_count

    def subscribe_windmill_network(self, network_id, listener):
        if network_id not in self._networks:
            raise KeyError(f"Unknown Golden Fields windmill network '{network_id}'.")
        self.game_objects.signals.subscribe(self.signal_name(network_id), listener)

    def unsubscribe_windmill_network(self, network_id, listener):
        self.game_objects.signals.unsubscribe(self.signal_name(network_id), listener)

    def _on_global_wind_changed(self, **kwargs):
        self.refresh()

    def _seed_windmill_states(self, config):
        """Create unvisited windmill state from its authored world default."""
        objects = self.game_objects.world_state.objects
        level_name = config["windmill_level"]
        if not objects.has_level(level_name):
            objects.init_level(level_name)

        for windmill_id, initial_state in config["windmill_initial_states"].items():
            objects.load_value(
                level_name, "windmill", windmill_id, initial=initial_state
            )

    def _calculate_turning_count(self, config):
        if not self.world_controller.is_enabled(self.world_controller.WIND_AVAILABLE):
            return 0

        objects = self.game_objects.world_state.objects
        return sum(
            objects.peek_value(
                config["windmill_level"], "windmill", windmill_id, default="idle"
            ) == "active"
            for windmill_id in config["windmill_ids"]
        )
