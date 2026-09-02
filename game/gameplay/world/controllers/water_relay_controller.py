"""Persistent, wind-powered water relay puzzles."""


class WaterRelayController:
    """Own relay state and publish the water currently available at each outlet.

    Relay visuals and water-reactive map objects are deliberately passive: they
    query this controller when they spawn and subscribe to its signal for later
    changes.  This keeps room reloads deterministic and avoids simulating water
    every frame.
    """

    SIGNAL_PREFIX = "water_relay:"
    WORLD_STATE_GROUP = "water_relay"
    VALID_ANGLES = (0, 90, 180, 270)

    def __init__(self, game_objects, world_controller):
        self.game_objects = game_objects
        self.world_controller = world_controller
        self._relays = {}

    @classmethod
    def signal_name(cls, relay_id):
        return f"{cls.SIGNAL_PREFIX}{relay_id}"

    def register(
        self,
        relay_id,
        *,
        state_level,
        wind_network,
        initial_angle=0,
        lever_signal_id=None,
    ):
        """Register a map-authored relay and return its current state.

        Multiple visuals for the same relay are allowed, but their puzzle
        configuration must be identical.
        """
        relay_id = str(relay_id)
        initial_angle = self._normalise_angle(initial_angle)
        config = {
            "state_level": str(state_level),
            "wind_network": str(wind_network),
            "initial_angle": initial_angle,
            "lever_signal_id": str(lever_signal_id or relay_id),
        }
        if not self.world_controller.golden_fields.is_registered_windmill_network(
            config["wind_network"]
        ):
            raise ValueError(
                f"Unknown wind network '{config['wind_network']}' for water relay '{relay_id}'."
            )

        previous = self._relays.get(relay_id)
        if previous is not None:
            if previous != config:
                raise ValueError(f"Water relay '{relay_id}' was registered with different settings.")
            return self.get_state(relay_id)

        self._relays[relay_id] = config
        objects = self.game_objects.world_state.objects
        if not objects.has_level(config["state_level"]):
            objects.init_level(config["state_level"])
        objects.load_bool(config["state_level"], self.WORLD_STATE_GROUP, relay_id, initial=False)
        objects.load_value(
            config["state_level"], self.WORLD_STATE_GROUP, self._angle_key(relay_id), initial=initial_angle
        )
        self.game_objects.signals.subscribe(config["lever_signal_id"], self._make_lever_listener(relay_id))
        self.world_controller.golden_fields.subscribe_windmill_network(
            config["wind_network"], self._make_wind_listener(relay_id)
        )
        return self.get_state(relay_id)

    def get_state(self, relay_id):
        relay_id = str(relay_id)
        config = self._config(relay_id)
        objects = self.game_objects.world_state.objects
        enabled = objects.load_bool(config["state_level"], self.WORLD_STATE_GROUP, relay_id)
        angle = self._normalise_angle(objects.load_value(
            config["state_level"], self.WORLD_STATE_GROUP, self._angle_key(relay_id), initial=config["initial_angle"]
        ))
        return {"relay_id": relay_id, "enabled": enabled, "angle": angle, "flowing": enabled and self._all_windmills_active(config)}

    def enable(self, relay_id):
        """Make a relay eligible to carry water after its ItemSocket is filled."""
        relay_id = str(relay_id)
        config = self._config(relay_id)
        state = self.get_state(relay_id)
        if state["enabled"]:
            return True

        self.game_objects.world_state.objects.set_bool(config["state_level"], self.WORLD_STATE_GROUP, relay_id, True)
        self._emit_state(relay_id)
        return True

    def rotate(self, relay_id, steps=1):
        relay_id = str(relay_id)
        config = self._config(relay_id)
        state = self.get_state(relay_id)
        if not state["enabled"]:
            return False
        angle = (state["angle"] + 90 * int(steps)) % 360
        self.game_objects.world_state.objects.set_value(
            config["state_level"], self.WORLD_STATE_GROUP, self._angle_key(relay_id), angle
        )
        self._emit_state(relay_id)
        return True

    def subscribe(self, relay_id, listener):
        self._config(str(relay_id))
        self.game_objects.signals.subscribe(self.signal_name(relay_id), listener)

    def unsubscribe(self, relay_id, listener):
        self.game_objects.signals.unsubscribe(self.signal_name(relay_id), listener)

    def _make_lever_listener(self, relay_id):
        def listener(*, action="toggle", **kwargs):
            if action == "enable":
                self.enable(relay_id)
            elif action in {"rotate", "rotate_clockwise"}:
                self.rotate(relay_id)
            elif action == "rotate_counterclockwise":
                self.rotate(relay_id, steps=-1)
        return listener

    def _make_wind_listener(self, relay_id):
        def listener(**kwargs):
            self._emit_state(relay_id)
        return listener

    def _emit_state(self, relay_id):
        self.game_objects.signals.emit(self.signal_name(relay_id), **self.get_state(relay_id))

    def _all_windmills_active(self, config):
        controller = self.world_controller.golden_fields
        return (
            controller.windmill_turning_count(config["wind_network"])
            == controller.windmill_network_size(config["wind_network"])
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
        if angle not in cls.VALID_ANGLES:
            raise ValueError("Water relay angles must be 0, 90, 180, or 270.")
        return angle
