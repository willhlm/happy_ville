import math

from engine.utils import read_files
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform


class LiftCar(DynamicPlatform):
    """A solid, switch-operated lift car that follows an ordered Tiled path.

    Cabin walls, doors, sounds, and cross-map choreography belong on this
    dedicated object as the lift grows.

    Tiled properties:
        signal_id: Signal channel the lift listens on. A lever with the same
            ``signal_id`` can command this lift.
        path: Object ID of an open polyline in the map's ``paths`` layer. Each
            polyline point is a possible station, in route order.
        lift_stations: Optional comma-separated names for those path points,
            in exactly the same order. For example, ``lower,middle,upper``.
            A lever sends one of these names as its ``value``.
        initial_station: Optional station name (or numeric path-point index)
            where the car starts. Without it, the car begins at the path point
            closest to its placed Tiled position.
        speed: Travel speed in pixels per second; default 80.

    If ``lift_stations`` is omitted, station indexes (``0``, ``1``, ...) work,
    and two-stop convenience names such as ``upper``/``lower`` and
    ``left``/``right`` select the relevant endpoint.
    """

    def __init__(self, pos, game_objects, **props):
        super().__init__(pos, game_objects)
        self.props = props
        self.signal_id = str(props.get("signal_id", props.get("id", ""))).strip()
        self.points = [tuple(point) for point in props.get("path_points") or ()]
        if not self.signal_id or len(self.points) < 2:
            raise ValueError("A lift requires signal_id and a path with at least two points")

        self.sprites = read_files.load_sprites_dict(f"assets/sprites/entities/platforms/liftcar/body/", game_objects)
        self.image = self.sprites["idle"][0]
        self.rect.size = [self.image.width, self.image.height]
        self.hitbox = self.rect.copy()
        self.old_hitbox = self.hitbox.copy()

        self.speed = max(0.0, float(props.get("speed", 80.0)) / 60.0)
        self.epsilon = max(0.0, float(props.get("arrival_epsilon", 0.5)))
        self.target_index = None

        raw_names = str(props.get("lift_stations", "")).strip()
        names = [name.strip() for name in raw_names.split(",") if name.strip()]
        if names and len(names) != len(self.points):
            raise ValueError(
                f"Lift {self.signal_id!r} has {len(self.points)} path points but "
                f"{len(names)} lift_stations entries"
            )
        self.has_named_stations = bool(names)
        self.station_names = names or [str(index) for index in range(len(self.points))]
        self.station_lookup = {name: index for index, name in enumerate(self.station_names)}
        self.current_index = self._resolve_initial_station()
        self._snap_to_point(self.current_index)
        self._subscribed = True
        self.game_objects.signals.subscribe(self.signal_id, self._on_signal)

    def kill(self):
        self.dispose()
        super().kill()

    def dispose(self):
        if self._subscribed:
            self.game_objects.signals.unsubscribe(self.signal_id, self._on_signal)
            self._subscribed = False

    def release_texture(self):
        """Called by the platform group while a map is being unloaded."""
        self.dispose()

    def get_support_motion(self, entity):
        return entity.platform_collider.get_support_motion(self)

    def _resolve_initial_station(self):
        requested = self.props.get("initial_station")
        if requested not in (None, ""):
            index = self._station_index(requested)
            if index is not None:
                return index
        x, y = self.true_pos
        return min(
            range(len(self.points)),
            key=lambda index: (self.points[index][0] - x) ** 2 + (self.points[index][1] - y) ** 2,
        )

    def _station_index(self, station):
        key = str(station).strip()
        if key in self.station_lookup:
            return self.station_lookup[key]
        if not self.has_named_stations:
            alias = key.lower()
            if alias in {"upper", "top"}:
                return min(range(len(self.points)), key=lambda index: self.points[index][1])
            if alias in {"lower", "bottom"}:
                return max(range(len(self.points)), key=lambda index: self.points[index][1])
            if alias == "left":
                return min(range(len(self.points)), key=lambda index: self.points[index][0])
            if alias == "right":
                return max(range(len(self.points)), key=lambda index: self.points[index][0])
        try:
            index = int(key)
        except (TypeError, ValueError):
            return None
        return index if 0 <= index < len(self.points) else None

    def _on_signal(self, action=None, value=None, **_kwargs):
        if action != "request_station":
            return
        index = self._station_index(value)
        if index is not None:
            self.target_index = index

    def _snap_to_point(self, index):
        x, y = self.points[index]
        self.true_pos[:] = [float(x), float(y)]
        self.rect.topleft = (round(x), round(y))
        self.hitbox.topleft = self.rect.topleft

    def update_vel(self, dt):
        self.velocity[0] = 0.0
        self.velocity[1] = 0.0
        if self.target_index is None or self.speed <= 0 or dt <= 0:
            return
        if self.target_index == self.current_index:
            self.target_index = None
            return

        direction = 1 if self.target_index > self.current_index else -1
        next_index = self.current_index + direction
        target_x, target_y = self.points[next_index]
        dx, dy = target_x - self.true_pos[0], target_y - self.true_pos[1]
        distance = math.hypot(dx, dy)
        if distance <= self.epsilon or self.speed * dt >= distance:
            self.velocity[0] = dx / dt
            self.velocity[1] = dy / dt
            self.current_index = next_index
            if self.current_index == self.target_index:
                self.target_index = None
            return

        self.velocity[0] = (dx / distance) * self.speed
        self.velocity[1] = (dy / distance) * self.speed

    def draw(self, target):
        self.game_objects.game.display.render(
            self.image,
            target,
            position=(
                int(self.rect.left - self.game_objects.camera_manager.camera.scroll[0]),
                int(self.rect.top - self.game_objects.camera_manager.camera.scroll[1]),
            ),
        )
