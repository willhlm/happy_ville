class SurfaceStickPhysics:
    CLOCKWISE_SURFACE_ORDER = ("bottom", "left", "top", "right")
    COUNTERCLOCKWISE_SURFACE_ORDER = ("bottom", "right", "top", "left")

    INWARD_VECTORS = {
        "bottom": (0, 1),
        "top": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }

    def __init__(self, entity, speed, stick_speed, probe_distance=2, corner_inset=3, clockwise=True, initial_side="bottom"):
        self.entity = entity
        self.speed = speed
        self.stick_speed = stick_speed
        self.probe_distance = probe_distance
        self.corner_inset = corner_inset
        self.clockwise = clockwise
        self.surface_side = initial_side if initial_side in self.INWARD_VECTORS else "bottom"
        self.surface_body = None

    def update_velocity(self, dt=None):
        self._refresh_surface()

        tangent = self._get_tangent_vector(self.surface_side)
        inward = self.INWARD_VECTORS[self.surface_side]

        self.entity.velocity[0] = tangent[0] * self.speed + inward[0] * self.stick_speed
        self.entity.velocity[1] = tangent[1] * self.speed + inward[1] * self.stick_speed

        if tangent[0] != 0:
            self.entity.dir[0] = 1 if tangent[0] > 0 else -1

    def post_physics_update(self, dt=None):
        if dt is not None and dt <= 0:
            return

        contact_state = self.entity.contact_state

        if contact_state.surface_collision:
            collision = contact_state.surface_collision
            self.surface_side = collision.side
            self.surface_body = collision.collider
            if self._snap_to_surface(self.surface_body, self.surface_side):
                return

            self._refresh_surface()
            return

        if self.surface_body is None:
            self._refresh_surface()
            return

        if self._try_wrap_current_surface():
            return

        self._reverse_direction()
        self._restore_to_surface(self.surface_body, self.surface_side)

    def handle_platform_collision(self, collision):
        if collision.side not in self.INWARD_VECTORS:
            return

        self.surface_side = collision.side
        self.surface_body = collision.collider
        if self._snap_to_surface(collision.collider, collision.side):
            return

    def get_angle(self):
        return {
            "bottom": 0,
            "left": -90,
            "top": 180,
            "right": 90,
        }[self.surface_side]

    def _refresh_surface(self):
        platform = self._find_platform_from_points(self._get_surface_probe_points(self.surface_side))
        if platform:
            self.surface_body = platform
            self._snap_to_surface(platform, self.surface_side)
            return

        for side in self.INWARD_VECTORS:
            platform = self._find_platform_from_points(self._get_surface_probe_points(side))
            if platform:
                self.surface_side = side
                self.surface_body = platform
                self._snap_to_surface(platform, side)
                return

    def _try_wrap_current_surface(self):
        next_side = self._get_next_side(self.surface_side)
        if not self._has_reached_corner(self.surface_body, self.surface_side):
            return False

        self._wrap_around_corner(self.surface_body, self.surface_side, next_side)
        self.surface_side = next_side
        self.surface_body = self.surface_body
        return True

    def _get_surface_probe_points(self, side):
        hitbox = self.entity.hitbox
        probe = self.probe_distance
        inset = min(self.corner_inset, max(1, min(hitbox.width, hitbox.height) // 2))

        if side == "bottom":
            return [
                (hitbox.left + inset, hitbox.bottom + probe),
                (hitbox.centerx, hitbox.bottom + probe),
                (hitbox.right - inset, hitbox.bottom + probe),
            ]
        if side == "top":
            return [
                (hitbox.left + inset, hitbox.top - probe),
                (hitbox.centerx, hitbox.top - probe),
                (hitbox.right - inset, hitbox.top - probe),
            ]
        if side == "left":
            return [
                (hitbox.left - probe, hitbox.top + inset),
                (hitbox.left - probe, hitbox.centery),
                (hitbox.left - probe, hitbox.bottom - inset),
            ]
        return [
            (hitbox.right + probe, hitbox.top + inset),
            (hitbox.right + probe, hitbox.centery),
            (hitbox.right + probe, hitbox.bottom - inset),
        ]

    def _get_tangent_vector(self, side):
        if self.clockwise:
            return {
                "bottom": (1, 0),
                "left": (0, 1),
                "top": (-1, 0),
                "right": (0, -1),
            }[side]

        return {
            "bottom": (-1, 0),
            "right": (0, 1),
            "top": (1, 0),
            "left": (0, -1),
        }[side]

    def _get_next_side(self, side):
        order = self.CLOCKWISE_SURFACE_ORDER if self.clockwise else self.COUNTERCLOCKWISE_SURFACE_ORDER
        index = order.index(side)
        return order[(index + 1) % len(order)]

    def _has_reached_corner(self, platform, side):
        if self._is_ramp(platform):
            return False

        hitbox = self.entity.hitbox
        inset = min(self.corner_inset, max(1, min(hitbox.width, hitbox.height) // 2))

        if side == "bottom":
            if self.clockwise:
                return hitbox.centerx >= platform.hitbox.right - inset
            return hitbox.centerx <= platform.hitbox.left + inset

        if side == "top":
            if self.clockwise:
                return hitbox.centerx <= platform.hitbox.left + inset
            return hitbox.centerx >= platform.hitbox.right - inset

        if side == "left":
            if self.clockwise:
                return hitbox.centery >= platform.hitbox.bottom - inset
            return hitbox.centery <= platform.hitbox.top + inset

        if self.clockwise:
            return hitbox.centery <= platform.hitbox.top + inset
        return hitbox.centery >= platform.hitbox.bottom - inset

    def _find_platform_from_points(self, points):
        for point in points:
            platform = self._find_platform_at_point(point)
            if platform:
                return platform
        return None

    def _find_platform_at_point(self, point):
        return self.entity.game_objects.physics.platform_spatial_index.query_point(point)

    def _wrap_around_corner(self, platform, from_side, to_side):
        hitbox = self.entity.hitbox

        if from_side == "bottom" and to_side == "left":
            hitbox.topleft = (platform.hitbox.right, platform.hitbox.top)
        elif from_side == "left" and to_side == "top":
            hitbox.topleft = (platform.hitbox.right - hitbox.width, platform.hitbox.bottom)
        elif from_side == "top" and to_side == "right":
            hitbox.topleft = (platform.hitbox.left - hitbox.width, platform.hitbox.bottom - hitbox.height)
        elif from_side == "right" and to_side == "bottom":
            hitbox.topleft = (platform.hitbox.left, platform.hitbox.top - hitbox.height)
        elif from_side == "bottom" and to_side == "right":
            hitbox.topleft = (platform.hitbox.left - hitbox.width, platform.hitbox.top)
        elif from_side == "right" and to_side == "top":
            hitbox.topleft = (platform.hitbox.left, platform.hitbox.bottom)
        elif from_side == "top" and to_side == "left":
            hitbox.topleft = (platform.hitbox.right, platform.hitbox.bottom - hitbox.height)
        elif from_side == "left" and to_side == "bottom":
            hitbox.topleft = (platform.hitbox.right - hitbox.width, platform.hitbox.top - hitbox.height)
        else:
            self._snap_to_surface(platform, to_side)
            return

        self.entity.body.update_rect_x()
        self.entity.body.update_rect_y()

    def _restore_to_surface(self, platform, side):
        hitbox = self.entity.hitbox

        if self._align_to_surface_target(platform, side):
            return

        if side == "bottom":
            hitbox.bottom = platform.hitbox.top
            hitbox.left = max(platform.hitbox.left, min(hitbox.left, platform.hitbox.right - hitbox.width))
        elif side == "top":
            hitbox.top = platform.hitbox.bottom
            hitbox.left = max(platform.hitbox.left, min(hitbox.left, platform.hitbox.right - hitbox.width))
        elif side == "left":
            hitbox.left = platform.hitbox.right
            hitbox.top = max(platform.hitbox.top, min(hitbox.top, platform.hitbox.bottom - hitbox.height))
        else:
            hitbox.right = platform.hitbox.left
            hitbox.top = max(platform.hitbox.top, min(hitbox.top, platform.hitbox.bottom - hitbox.height))

        self.entity.body.update_rect_x()
        self.entity.body.update_rect_y()

    def _reverse_direction(self):
        self.clockwise = not self.clockwise

    def _snap_to_surface(self, platform, side):
        if self._align_to_surface_target(platform, side):
            return True

        if self._is_ramp(platform):
            return False

        if side == "bottom":
            self.entity.hitbox.bottom = platform.hitbox.top
            self.entity.body.update_rect_y()
            return True

        if side == "top":
            self.entity.hitbox.top = platform.hitbox.bottom
            self.entity.body.update_rect_y()
            return True

        if side == "left":
            self.entity.hitbox.left = platform.hitbox.right
            self.entity.body.update_rect_x()
            return True

        self.entity.hitbox.right = platform.hitbox.left
        self.entity.body.update_rect_x()
        return True

    def _align_to_surface_target(self, platform, side):
        if not self._is_ramp(platform):
            return False

        surface_collision = getattr(platform, "surface_collision", None)
        if surface_collision is None:
            return False

        if side == "bottom":
            target = surface_collision._get_floor_target(self.entity.hitbox)
            if target is None:
                return False
            self.entity.hitbox.bottom = target
            self.entity.body.update_rect_y()
            return True

        if side == "top":
            target = surface_collision._get_ceiling_target(self.entity.hitbox)
            if target is None:
                return False
            self.entity.hitbox.top = target
            self.entity.body.update_rect_y()
            return True

        return False

    @staticmethod
    def _is_ramp(platform):
        return getattr(platform, "surface_collision", None).__class__.__name__ == "RightAngleSurfaceCollisionComponent"
