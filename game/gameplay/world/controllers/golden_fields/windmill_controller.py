"""Golden Fields windmill networks and their persistent activation state."""

from gameplay.world.configs.golden_fields_systems import WINDMILL_NETWORKS


class WindmillController:
    """Publish binary power only when every windmill in a network is active."""

    SIGNAL_PREFIX = "golden_fields:windmill_network:"
    ACTIVATION_SIGNAL = "golden_fields:activate_windmill"

    def __init__(self, game_objects, world_controller, power_controller):
        self.game_objects = game_objects
        self.world_controller = world_controller
        self.power_controller = power_controller
        self._networks = {}
        self._powered = {}

        for network_id, config in WINDMILL_NETWORKS.items():
            self.register(network_id, **config)
        self.game_objects.signals.subscribe(
            self.ACTIVATION_SIGNAL,
            self._on_windmill_activation,
        )
        self.world_controller.subscribe(
            self.world_controller.WIND_AVAILABLE,
            self._on_global_wind_changed,
        )

    @classmethod
    def signal_name(cls, network_id):
        return f"{cls.SIGNAL_PREFIX}{network_id}"

    def register(
        self,
        network_id,
        *,
        windmill_level,
        windmill_ids,
        windmill_initial_states=None,
    ):
        network_id = str(network_id)
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
        previous = self._networks.get(network_id)
        if previous is not None:
            if previous != config:
                raise ValueError(
                    f"Windmill network '{network_id}' was registered with "
                    "different settings."
                )
            return self._powered[network_id]

        self._networks[network_id] = config
        self._seed_windmill_states(config)
        self._powered[network_id] = self._calculate_power(config)
        self.power_controller.register_source(
            network_id,
            lambda network_id=network_id, **requirements: self.is_powered(
                network_id
            ),
            subscribe=lambda listener, network_id=network_id: self.subscribe(
                network_id, listener
            ),
            unsubscribe=lambda listener, network_id=network_id: self.unsubscribe(
                network_id, listener
            ),
        )
        return self._powered[network_id]

    def is_registered(self, network_id):
        return str(network_id) in self._networks

    def is_powered(self, network_id):
        try:
            return self._powered[str(network_id)]
        except KeyError as error:
            raise KeyError(f"Unknown windmill network '{network_id}'.") from error

    def active_count(self, network_id):
        """Return the number of active windmills currently producing power."""
        network_id = str(network_id)
        try:
            config = self._networks[network_id]
        except KeyError as error:
            raise KeyError(f"Unknown windmill network '{network_id}'.") from error
        return self._calculate_active_count(config)

    def activate(self, windmill_id):
        """Persistently activate an authored windmill by its network ID."""
        windmill_id = str(windmill_id)
        matches = [
            config
            for config in self._networks.values()
            if windmill_id in config["windmill_ids"]
        ]
        if len(matches) != 1:
            raise KeyError(
                f"Unknown or ambiguous Golden Fields windmill '{windmill_id}'."
            )
        config = matches[0]
        self.game_objects.world_state.objects.set_value(
            config["windmill_level"],
            "windmill",
            windmill_id,
            "active",
        )
        self.game_objects.signals.emit(windmill_id, state="active")
        self.refresh()

    def refresh(self):
        return {
            network_id: self.refresh_network(network_id)
            for network_id in tuple(self._networks)
        }

    def refresh_network(self, network_id):
        try:
            config = self._networks[network_id]
        except KeyError as error:
            raise KeyError(f"Unknown windmill network '{network_id}'.") from error

        powered = self._calculate_power(config)
        previously_powered = self._powered[network_id]
        self._powered[network_id] = powered
        if powered != previously_powered:
            self.game_objects.signals.emit(
                self.signal_name(network_id),
                network_id=network_id,
                powered=powered,
            )
        return powered

    def subscribe(self, network_id, listener):
        if network_id not in self._networks:
            raise KeyError(f"Unknown windmill network '{network_id}'.")
        self.game_objects.signals.subscribe(self.signal_name(network_id), listener)

    def unsubscribe(self, network_id, listener):
        self.game_objects.signals.unsubscribe(self.signal_name(network_id), listener)

    def _on_windmill_activation(self, *, action, value, **kwargs):
        if action == "activate":
            self.activate(value)

    def _on_global_wind_changed(self, **kwargs):
        self.refresh()

    def _seed_windmill_states(self, config):
        objects = self.game_objects.world_state.objects
        level_name = config["windmill_level"]
        if not objects.has_level(level_name):
            objects.init_level(level_name)

        for windmill_id, initial_state in config["windmill_initial_states"].items():
            objects.load_value(
                level_name,
                "windmill",
                windmill_id,
                initial=initial_state,
            )

    def _calculate_power(self, config):
        return self._calculate_active_count(config) == len(config["windmill_ids"])

    def _calculate_active_count(self, config):
        if not self.world_controller.is_enabled(
            self.world_controller.WIND_AVAILABLE
        ):
            return 0

        objects = self.game_objects.world_state.objects
        return sum(
            objects.peek_value(
                config["windmill_level"],
                "windmill",
                windmill_id,
                default="idle",
            ) == "active"
            for windmill_id in config["windmill_ids"]
        )
