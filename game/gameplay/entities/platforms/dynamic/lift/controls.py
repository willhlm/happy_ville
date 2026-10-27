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


def attach_boarding_control(lift, props):
    """Attach an enter-to-go area to a two-station lift."""
    if len(lift.points) != 2:
        raise ValueError("An enter-to-go lift requires exactly two path points")
    default_offset = (
        lift.hitbox.left - lift.rect.left,
        lift.hitbox.top - lift.rect.top - 16,
    )
    default_size = (lift.hitbox.width, lift.hitbox.height + 16)
    trigger = LiftBoardingTrigger(
        lift,
        parse_pair(props.get("boarding_offset"), default_offset),
        parse_pair(props.get("boarding_size"), default_size),
    )
    lift.game_objects.interactables_bg.add(trigger)
    lift.attach(trigger)
    return trigger


def attach_controls(lift, props):
    """Attach the control described by a normal ``LiftCar``'s props."""
    mode = str(props.get("control_mode", "signal")).strip().lower()
    if mode == "signal":
        pass
    elif mode == "mounted_lever":
        default = (lift.rect.width // 2, lift.rect.height // 2)
        lever = LiftMountedLever(lift, parse_pair(props.get("lever_offset"), default))
        lift.game_objects.interactables_bg.add(lever)
        lift.attach(lever)
    elif mode == "enter_to_go":
        attach_boarding_control(lift, props)
    else:
        raise ValueError(f"Unknown lift control_mode: {mode!r}")
