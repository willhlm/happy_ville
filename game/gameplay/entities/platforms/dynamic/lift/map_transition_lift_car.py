from .controls import attach_boarding_control
from .lift_car import LiftCar


class MapTransitionController:
    """Start a map handoff when a transition lift reaches station 1."""

    def __init__(self, lift):
        self.lift = lift
        self.started = False
        lift.add_arrival_listener(self._on_arrival)

    def _on_arrival(self, _lift, station_index):
        if self.started or station_index != 1:
            return
        self.started = True
        self.lift.game_objects.sequence_manager.start_sequence(
            "lift_traversal",
            destination=self.lift.destination_map,
            destination_lift_id=self.lift.destination_lift_id,
            previous_state=self.lift.game_objects.game.state_manager.state_stack[-1],
        )


class MapTransitionLiftCar(LiftCar):
    """A two-station lift cabin that carries the player between maps.

    This lift inherits the movement, path, power, and signal properties from
    ``LiftCar``. It always uses an enter-to-go boarding area and does not use
    ``control_mode``.

    Additional required Tiled properties:
        lift_id:
            Identity used by an arriving traversal to find this car.
        destination_map:
            Map loaded when the car reaches boundary station ``1``.
        destination_lift_id:
            ``lift_id`` of the matching ``MapTransitionLiftCar`` in the
            destination map.

    Optional Tiled properties:
        boarding_offset:
            ``x,y`` offset of the boarding area from the car's top-left.
        boarding_size:
            ``width,height`` of the boarding area. By default it matches the
            car hitbox and extends 16 pixels above it.

    The path must contain exactly two stations: ``0`` is the interior stop and
    ``1`` is the map boundary. A traversal places the matching destination car
    at station ``1`` and immediately sends it to station ``0``.
    """

    SPRITE_PATH = "assets/sprites/entities/platforms/lifts/liftcar/body/"

    def __init__(self, pos, game_objects, **props):
        required = ("lift_id", "destination_map", "destination_lift_id")
        missing = [key for key in required if props.get(key) in (None, "")]
        if missing:
            raise ValueError(
                f"A map-transition lift requires: {', '.join(missing)}"
            )

        if len(props.get("path_points") or ()) != 2:
            raise ValueError(
                "A map-transition lift requires exactly two path points"
            )

        self.lift_id = str(props["lift_id"])
        self.destination_map = str(props["destination_map"])
        self.destination_lift_id = str(props["destination_lift_id"])

        super().__init__(pos, game_objects, self.SPRITE_PATH, **props)
        attach_boarding_control(self, props)
        self.map_transition_controller = MapTransitionController(self)
