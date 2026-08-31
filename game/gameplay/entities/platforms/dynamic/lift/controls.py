import pygame

from gameplay.entities.areas.base import BaseArea
from gameplay.entities.interactables.lever.lever import Lever


def parse_pair(value, default):
    """Read a Tiled ``x,y`` property into an integer pair."""
    if value in (None, ""):
        return default
    if isinstance(value, (tuple, list)):
        return int(value[0]), int(value[1])
    x, y = str(value).split(",", 1)
    return int(x.strip()), int(y.strip())


class LiftMountedLever(Lever):
    """A lever sprite attached to a LiftCar in this dynamic-platform package."""

    def __init__(self, lift, offset):
        self.lift = lift
        self.offset = offset
        super().__init__((0, 0), lift.game_objects, signal_id=f"{lift.signal_id}:mounted")
        self.sync_position()

    def sync_position(self):
        self.rect.topleft = (
            self.lift.rect.left + self.offset[0],
            self.lift.rect.top + self.offset[1],
        )
        self.hitbox.topleft = self.rect.topleft
        self.true_pos = list(self.rect.topleft)

    def take_dmg(self, effect):
        self.currentstate.handle_input("Transform")
        self.lift.press_mounted_lever()
        return effect


class LiftBoardingTrigger(BaseArea):
    """An invisible child area that starts a two-stop lift when entered."""

    def __init__(self, lift, offset, size):
        self.lift = lift
        self.offset = offset
        self.size = size
        super().__init__((0, 0), lift.game_objects)
        self.rect = pygame.Rect(0, 0, *size)
        self.hitbox = self.rect.copy()
        self.sync_position()

    def sync_position(self):
        self.rect.topleft = (
            self.lift.rect.left + self.offset[0],
            self.lift.rect.top + self.offset[1],
        )
        self.hitbox.topleft = self.rect.topleft
        self.true_pos = list(self.rect.topleft)

    def on_collision(self, player):
        self.lift.boarded(player)


class LiftMapTransitionControl:
    """Starts a map handoff once a mounted-lever lift reaches its terminal."""

    def __init__(self, lift, props):
        self.lift = lift
        self.destination_map = str(props["destination_map"])
        self.destination_lift_id = str(props["destination_lift_id"])
        self.destination_station = props.get("destination_station", 0)
        self.destination_continue_to = props.get("destination_continue_to")
        self.transition_station = int(props.get("transition_station", len(lift.points) - 1))
        direction = props.get("transition_direction")
        self.transition_direction = None if direction in (None, "") else lift._parse_direction(direction)
        self.started = False
        lift.add_arrival_listener(self._on_arrival)

    def _on_arrival(self, _lift, station_index):
        if self.started or station_index != self.transition_station:
            return
        if self.transition_direction is not None and self.lift.travel_direction != self.transition_direction:
            return
        self.started = True
        self.lift.game_objects.sequence_manager.start_sequence(
            "lift_traversal",
            destination=self.destination_map,
            destination_lift_id=self.destination_lift_id,
            destination_station=self.destination_station,
            destination_continue_to=self.destination_continue_to,
            previous_state=self.lift.game_objects.game.state_manager.state_stack[-1],
        )


def attach_controls(lift, props):
    """Create the configured lift controls at map-assembly time.

    Keeping this outside ``LiftCar`` prevents platform imports from depending
    on the interactable and area packages used by the controls.

    Tiled control properties:
        control_mode: ``signal`` adds no child control; ``mounted_lever`` adds
            a hit-operated lever; ``enter_to_go`` adds an invisible boarding
            trigger; ``map_transition`` adds a mounted lever plus map handoff.
        lever_offset: Optional ``x,y`` position of a mounted lever relative
            to the car's top-left. It defaults to the car centre.
        boarding_offset / boarding_size: Optional ``x,y`` and ``width,height``
            of the enter-to-go trigger. They default to the full car.
        destination_map / destination_lift_id: Required for ``map_transition``.
            They identify the map to load and the matching destination car.
        destination_station: Station where that destination car is docked.
        destination_continue_to: Optional station it starts travelling toward
            immediately after the player is placed on it.
        transition_station: Source station that triggers the map handoff;
            defaults to the final path point.
        transition_direction: Optional ``1`` or ``-1`` requirement. This lets
            one endpoint distinguish arriving from departing at the same stop.
    """
    mode = str(props.get("control_mode", "signal")).strip().lower()
    if mode == "signal":
        return
    if mode == "mounted_lever":
        default = (lift.rect.width // 2, lift.rect.height // 2)
        lever = LiftMountedLever(lift, parse_pair(props.get("lever_offset"), default))
        lift.game_objects.interactables.add(lever)
        lift.attach(lever)
        return
    if mode == "map_transition":
        required = ("destination_map", "destination_lift_id")
        missing = [key for key in required if props.get(key) in (None, "")]
        if missing:
            raise ValueError(f"A map_transition lift requires: {', '.join(missing)}")
        default = (lift.rect.width // 2, lift.rect.height // 2)
        lever = LiftMountedLever(lift, parse_pair(props.get("lever_offset"), default))
        lift.game_objects.interactables.add(lever)
        lift.attach(lever)
        LiftMapTransitionControl(lift, props)
        return
    if mode == "enter_to_go":
        if len(lift.points) != 2:
            raise ValueError("An enter_to_go lift requires exactly two path points")
        trigger = LiftBoardingTrigger(
            lift,
            parse_pair(props.get("boarding_offset"), (0, 0)),
            parse_pair(props.get("boarding_size"), (lift.rect.width, lift.rect.height)),
        )
        lift.game_objects.interactables.add(trigger)
        lift.attach(trigger)
        return
    raise ValueError(f"Unknown lift control_mode: {mode!r}")
