import math
from engine.utils import read_files
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform
from gameplay.entities.platforms.pathing import centre_path_to_topleft

class LiftCar(DynamicPlatform):
    """A solid, switch-operated lift car that follows an ordered Tiled path.

    Cabin walls, doors, sounds, and cross-map choreography belong on this
    dedicated object as the lift grows.

    Tiled properties:
        signal_id: Signal channel the lift listens on. A lever with the same
            ``signal_id`` can command this lift.
        lift_id: Optional identity for matching this car with a car in another
            map during a ``map_transition`` ride.
        path: Object ID of an open polyline in the map's ``paths`` layer. Each
            polyline point is a possible station, in route order, and marks
            the centre of the lift car.
        lift_stations: Optional comma-separated names for those path points,
            in exactly the same order. For example, ``lower,middle,upper``.
            A lever sends one of these names as its ``value``.
        initial_station: Optional station name (or numeric path-point index)
            where the car starts. Without it, the car begins at the path point
            closest to its placed Tiled position.
        speed: Travel speed in pixels per second; default 80.
        arrival_epsilon: Distance within which a car is treated as docked;
            default 0.5 pixels.
        station_direction: Initial travel direction for a mounted lever:
            ``1``/forward (default) or ``-1``/reverse.
        Control properties are interpreted by the map-level lift assembler,
        rather than by this platform class. This keeps travel physics separate
        from interactable and area dependencies.

    If ``lift_stations`` is omitted, station indexes (``0``, ``1``, ...) work,
    and two-stop convenience names such as ``upper``/``lower`` and
    ``left``/``right`` select the relevant endpoint.
    """

    def __init__(self, pos, game_objects, sprite_path, **props):
        super().__init__(pos, game_objects)
        self.props = props
        self.signal_id = str(props.get("signal_id", props.get("id", ""))).strip()
        self.lift_id = str(props.get("lift_id", "")).strip() or None
        path_points = [tuple(point) for point in props.get("path_points") or ()]
        if not self.signal_id or len(path_points) < 2:
            raise ValueError("A lift requires signal_id and a path with at least two points")

        self.sprites = read_files.load_sprites_dict(sprite_path, game_objects)
        self.image = self.sprites["idle"][0]
        self.rect.size = [self.image.width, self.image.height]
        self.hitbox = self.rect.copy()
        self.old_hitbox = self.hitbox.copy()

        # Tiled paths describe the centre of the cabin. Physics still uses a
        # top-left position, so convert each station once at construction.
        self.points = centre_path_to_topleft(path_points, self.rect.size)

        self.speed = max(0.0, float(props.get("speed", 80.0)) / 60.0)
        self.epsilon = max(0.0, float(props.get("arrival_epsilon", 0.5)))
        self.destination_index = None
        self.segment_target_index = None
        self.travel_direction = self._parse_direction(props.get("station_direction", 1))
        self.arrival_listeners = []
        self._arrived_index = None

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
        self.attachments = []

    def kill(self):
        self.dispose()
        super().kill()

    def dispose(self):
        if self._subscribed:
            self.game_objects.signals.unsubscribe(self.signal_id, self._on_signal)
            self._subscribed = False
        for attachment in self.attachments:
            attachment.kill()
        self.attachments = []

    def release_texture(self):
        """Called by the platform group while a map is being unloaded."""
        self.dispose()

    def get_support_motion(self, entity):
        return entity.platform_collider.get_support_motion(self)

    @property
    def is_travelling(self):
        return self.segment_target_index is not None

    def attach(self, attachment):
        """Register a child object that follows this car's position."""
        self.attachments.append(attachment)
        attachment.sync_position()

    def add_arrival_listener(self, listener):
        """Call ``listener(lift, station_index)`` after the car docks."""
        self.arrival_listeners.append(listener)

    def place_at_station(self, station):
        """Dock immediately at a station; used when a map-transition ride arrives."""
        index = self._station_index(station)
        if index is None:
            raise ValueError(f"Unknown station {station!r} for lift {self.signal_id!r}")
        if self.is_travelling:
            raise RuntimeError("Cannot place a lift while it is travelling")
        self.current_index = index
        self._snap_to_point(index)
        for attachment in self.attachments:
            attachment.sync_position()

    @staticmethod
    def _parse_direction(value):
        return -1 if str(value).strip() in {"-1", "backward", "reverse"} else 1

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
            self.request_station(index)

    def request_station(self, index):
        """Travel to a requested station when docked.

        Explicit external station commands deliberately do nothing during a
        journey. Mounted controls use ``press_mounted_lever`` for reversal.
        """
        if self.is_travelling or index == self.current_index:
            return False
        self.destination_index = index
        self._start_next_segment()
        return True

    def press_mounted_lever(self):
        """Advance at a station; reverse toward the previous station in transit."""
        if self.is_travelling:
            self.travel_direction *= -1
            self.destination_index = self.current_index
            self.segment_target_index = self.current_index
            return

        next_index = self.current_index + self.travel_direction
        if not 0 <= next_index < len(self.points):
            self.travel_direction *= -1
            next_index = self.current_index + self.travel_direction
        self.request_station(next_index)

    def boarded(self, _player):
        """Start an enter-to-go lift toward its other station."""
        if self.is_travelling:
            return
        self.request_station(1 - self.current_index)

    def _start_next_segment(self):
        if self.destination_index == self.current_index:
            self.destination_index = None
            self.segment_target_index = None
            return
        self.travel_direction = 1 if self.destination_index > self.current_index else -1
        self.segment_target_index = self.current_index + self.travel_direction

    def _snap_to_point(self, index):
        x, y = self.points[index]
        self.true_pos[:] = [float(x), float(y)]
        self.rect.topleft = (round(x), round(y))
        self.hitbox.topleft = self.rect.topleft

    def update_vel(self, dt):
        self.velocity[0] = 0.0
        self.velocity[1] = 0.0
        if not self.is_travelling or self.speed <= 0 or dt <= 0:
            return

        target_x, target_y = self.points[self.segment_target_index]
        dx, dy = target_x - self.true_pos[0], target_y - self.true_pos[1]
        distance = math.hypot(dx, dy)
        if distance <= self.epsilon or self.speed * dt >= distance:
            self.velocity[0] = dx / dt
            self.velocity[1] = dy / dt
            self.current_index = self.segment_target_index
            self._arrived_index = self.current_index
            self.segment_target_index = None
            if self.current_index == self.destination_index:
                self.destination_index = None
            else:
                self._start_next_segment()
            return

        self.velocity[0] = (dx / distance) * self.speed
        self.velocity[1] = (dy / distance) * self.speed

    def end_step(self):
        super().end_step()
        for attachment in self.attachments:
            attachment.sync_position()
        if self._arrived_index is not None:
            arrived_index = self._arrived_index
            self._arrived_index = None
            for listener in tuple(self.arrival_listeners):
                listener(self, arrived_index)

    def draw(self, target):
        self.game_objects.game.display.render(
            self.image,
            target,
            position=(
                int(self.rect.left - self.game_objects.camera_manager.camera.scroll[0]),
                int(self.rect.top - self.game_objects.camera_manager.camera.scroll[1]),
            ),
        )
