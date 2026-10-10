"""Golden Fields water relay puzzle state and power-source provider."""

from gameplay.world.configs.golden_fields_systems import (
    WATER_RELAY_ANGLES,
    WATER_RELAYS,
)


class WaterRelayController:
    """Own persistent relay state and publish each directed water outlet."""

    SIGNAL_PREFIX = "water_relay:"
    WORLD_STATE_GROUP = "water_relay"

    def __init__(
        self,
        game_objects,
        world_controller,
        power_controller,
        windmill_controller,
    ):
        self.game_objects = game_objects
        self.world_controller = world_controller
        self.power_controller = power_controller
        self.windmill_controller = windmill_controller
        self._relays = {}
        for relay_id, config in WATER_RELAYS.items():
            self.register(relay_id, **config)

    @classmethod
    def signal_name(cls, relay_id):
        return f"{cls.SIGNAL_PREFIX}{relay_id}"

    def register(
        self,
        relay_id,
        *,
        state_level,
        power_source,
        initial_angle=0,
        lever_signal_id=None,
    ):
        """Register a wind-powered relay and return its current state."""
        relay_id = str(relay_id)
        initial_angle = self._normalise_angle(initial_angle)
        config = {
            "state_level": str(state_level),
            "power_source": str(power_source),
            "initial_angle": initial_angle,
            "lever_signal_id": str(lever_signal_id or relay_id),
        }
        if not self.windmill_controller.is_registered(config["power_source"]):
            raise ValueError(
                f"Unknown windmill power source '{config['power_source']}' "
                f"for water relay '{relay_id}'."
            )

        previous = self._relays.get(relay_id)
        if previous is not None:
            if previous != config:
                raise ValueError(
                    f"Water relay '{relay_id}' was registered with different settings."
                )
            return self.get_state(relay_id)

        self._relays[relay_id] = config
        objects = self.game_objects.world_state.objects
        if not objects.has_level(config["state_level"]):
            objects.init_level(config["state_level"])
        objects.load_bool(
            config["state_level"],
            self.WORLD_STATE_GROUP,
            relay_id,
            initial=False,
        )
        objects.load_value(
            config["state_level"],
            self.WORLD_STATE_GROUP,
            self._angle_key(relay_id),
            initial=initial_angle,
        )
        self.game_objects.signals.subscribe(
            config["lever_signal_id"],
            self._make_lever_listener(relay_id),
        )
        self.power_controller.subscribe(
            config["power_source"],
            self._make_power_listener(relay_id),
        )
        self.power_controller.register_source(
            relay_id,
            lambda relay_id=relay_id, **requirements: self._resolve_power(
                relay_id,
                **requirements,
            ),
            subscribe=lambda listener, relay_id=relay_id: self.subscribe(
                relay_id, listener
            ),
            unsubscribe=lambda listener, relay_id=relay_id: self.unsubscribe(
                relay_id, listener
            ),
        )
        return self.get_state(relay_id)

    def get_state(self, relay_id):
        relay_id = str(relay_id)
        config = self._config(relay_id)
        objects = self.game_objects.world_state.objects
        enabled = objects.load_bool(
            config["state_level"],
            self.WORLD_STATE_GROUP,
            relay_id,
        )
        angle = self._normalise_angle(
            objects.load_value(
                config["state_level"],
                self.WORLD_STATE_GROUP,
                self._angle_key(relay_id),
                initial=config["initial_angle"],
            )
        )
        return {
            "relay_id": relay_id,
            "enabled": enabled,
            "angle": angle,
            "flowing": enabled
            and self.power_controller.is_powered(config["power_source"]),
        }

    def is_registered(self, relay_id):
        return str(relay_id) in self._relays

    def is_flowing_to(self, relay_id, angle):
        state = self.get_state(relay_id)
        return state["flowing"] and state["angle"] == self._normalise_angle(angle)

    def enable(self, relay_id):
        relay_id = str(relay_id)
        config = self._config(relay_id)
        state = self.get_state(relay_id)
        if state["enabled"]:
            return True

        self.game_objects.world_state.objects.set_bool(
            config["state_level"],
            self.WORLD_STATE_GROUP,
            relay_id,
            True,
        )
        self._emit_state(relay_id)
        return True

    def rotate(self, relay_id, steps=1):
        relay_id = str(relay_id)
        config = self._config(relay_id)
        state = self.get_state(relay_id)
        if not state["enabled"]:
            return False
        angle_index = WATER_RELAY_ANGLES.index(state["angle"])
        angle = WATER_RELAY_ANGLES[
            (angle_index + int(steps)) % len(WATER_RELAY_ANGLES)
        ]
        self.game_objects.world_state.objects.set_value(
            config["state_level"],
            self.WORLD_STATE_GROUP,
            self._angle_key(relay_id),
            angle,
        )
        self._emit_state(relay_id)
        return True

    def subscribe(self, relay_id, listener):
        self._config(str(relay_id))
        self.game_objects.signals.subscribe(self.signal_name(relay_id), listener)

    def unsubscribe(self, relay_id, listener):
        self.game_objects.signals.unsubscribe(self.signal_name(relay_id), listener)

    def _resolve_power(self, relay_id, *, relay_angle=None, **requirements):
        if relay_angle is None:
            raise ValueError(
                f"Water relay power source '{relay_id}' requires relay_angle."
            )
        return self.is_flowing_to(relay_id, relay_angle)

    def _make_lever_listener(self, relay_id):
        def listener(*, action="toggle", **kwargs):
            if action == "enable":
                self.enable(relay_id)
            elif action in {"rotate", "rotate_clockwise"}:
                self.rotate(relay_id)
            elif action == "rotate_counterclockwise":
                self.rotate(relay_id, steps=-1)

        return listener

    def _make_power_listener(self, relay_id):
        def listener(**kwargs):
            self._emit_state(relay_id)

        return listener

    def _emit_state(self, relay_id):
        self.game_objects.signals.emit(
            self.signal_name(relay_id),
            **self.get_state(relay_id),
        )

    def _config(self, relay_id):
        try:
            return self._relays[relay_id]
        except KeyError as error:
            raise KeyError(f"Unknown water relay '{relay_id}'.") from error

    @classmethod
    def _angle_key(cls, relay_id):
        return f"{relay_id}:angle"

    @classmethod
    def _normalise_angle(cls, angle):
        angle = int(angle) % 360
        if angle not in WATER_RELAY_ANGLES:
            valid_angles = ", ".join(str(value) for value in WATER_RELAY_ANGLES)
            raise ValueError(f"Water relay angles must be one of: {valid_angles}.")
        return angle
