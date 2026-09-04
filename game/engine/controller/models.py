from dataclasses import dataclass


@dataclass(frozen=True)
class AxesSnapshot:
    move: tuple[float, float]
    look: tuple[float, float]
    dpad: tuple[int, int]
    l_trigger: float
    r_trigger: float


@dataclass(frozen=True)
class InputFrame:
    axes: AxesSnapshot
    pressed: frozenset[str]
    released: frozenset[str]
    held: frozenset[str]
    dt: float


class InputAction:
    def __init__(self, name, pressed=False, released=False, axes=None, lifetime=10):
        self.name = name
        self.pressed = pressed
        self.released = released
        self.axes = axes or AxesSnapshot((0, 0), (0, 0), (0, 0), 0, 0)
        self.lifetime = lifetime
        self.meta = {}
        self.is_done = False

    def update(self, dt):
        if self.is_done:
            return
        self.lifetime -= dt
        if self.lifetime < 0:
            self.processed()

    def processed(self):
        self.is_done = True
