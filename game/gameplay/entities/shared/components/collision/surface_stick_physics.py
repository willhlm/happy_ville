from engine.utils.functions import sign
from gameplay.entities.common.surface_side import SURFACE_ANGLE_BY_SIDE, SURFACE_SIDES

class NullSurfaceStickPhysics:
    def __init__(self, entity):
        self.entity = entity
        self.surface_side = "bottom"

    def set_enabled(self, enabled=True):
        return None

    def is_enabled(self):
        return False

    def update_surface(self):
        return None

    def post_physics_update(self, dt=None):
        return None

    def handle_platform_collision(self, collision):
        return None

    def get_angle(self):
        return 0

    def get_tangent_vector(self):
        return (self.entity.dir[0], 0)

    def get_inward_vector(self):
        return (0, 1)

    def reverse_direction(self):
        self.entity.dir[0] *= -1

    def set_direction_towards(self, target_pos):
        desired = sign(target_pos[0] - self.entity.hitbox.centerx)
        if desired:
            self.entity.dir[0] = desired

    def detach(self):
        return None

    def attach_from_collision(self, collision, snap=False):
        return False

    def has_surface(self):
        return False

    def get_blocked_edge_ahead(self, lookahead=0):
        return None


class SurfaceStickPhysics:
    CLOCKWISE_SURFACE_ORDER = ("bottom", "left", "top", "right")
    COUNTERCLOCKWISE_SURFACE_ORDER = ("bottom", "right", "top", "left")

    INWARD_VECTORS = {
        "bottom": (0, 1),
        "top": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }

    def __init__(self, entity, probe_distance=2, corner_inset=3, clockwise=True, initial_side="bottom"):
        self.entity = entity
        self.probe_distance = probe_distance
        self.corner_inset = corner_inset
        self.clockwise = clockwise
        self.enabled = True
        self.freefall_gravity = entity.acceleration[1]
        self.surface_side = initial_side
        self.surface_body = None

    def set_enabled(self, enabled=True):
        self.enabled = enabled
        self.entity.acceleration[1] = 0 if enabled else self.freefall_gravity
        if not enabled:
            self.detach()

    def is_enabled(self):
        return self.enabled

    def update_surface(self):
        if not self.enabled:
            return
        self._refresh_surface()

    def get_tangent_vector(self):
        return self._get_tangent_vector(self.surface_side)

    def get_inward_vector(self):
        return self.INWARD_VECTORS[self.surface_side]

    def set_direction_towards(self, target_pos):
        dx = target_pos[0] - self.entity.hitbox.centerx
        dy = target_pos[1] - self.entity.hitbox.centery

        if self.surface_side == "bottom" and dx != 0:
            self.clockwise = dx > 0
        elif self.surface_side == "top" and dx != 0:
            self.clockwise = dx < 0
        elif self.surface_side == "left" and dy != 0:
            self.clockwise = dy > 0
        elif self.surface_side == "right" and dy != 0:
            self.clockwise = dy < 0

    def reverse_direction(self):
        self.clockwise = not self.clockwise

    def post_physics_update(self, dt):
        if not self.enabled:
            return
        if dt <= 0:
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

        self._restore_to_surface(self.surface_body, self.surface_side)

    def handle_platform_collision(self, collision):
        if not self.enabled:
            return
        if collision.side not in self.INWARD_VECTORS:
            return
        if not self._can_stick_to_platform(collision.collider, collision.side):
            return

        self.surface_side = collision.side
        self.surface_body = collision.collider
        if self._snap_to_surface(collision.collider, collision.side):
            return

    def get_angle(self):
        return SURFACE_ANGLE_BY_SIDE[self.surface_side]

    def detach(self):
        self.entity.acceleration[1] = self.freefall_gravity
        self.surface_body = None

    def attach_from_collision(self, collision, snap=False):
        if collision.side not in self.INWARD_VECTORS:
            return False
        if not self._can_stick_to_platform(collision.collider, collision.side):
            return False

        self.surface_side = collision.side
        self.surface_body = collision.collider
        self.entity.acceleration[1] = 0
        if snap:
            return self._snap_to_surface(collision.collider, collision.side)
        return True

    def has_surface(self):
        return self.surface_body is not None

    def get_blocked_edge_ahead(self, lookahead=0):
        if not self.enabled:
            return None
        if self.surface_body is None:
            return None

        next_side = self._get_next_side(self.surface_side)
        if self._can_stick_to_platform(self.surface_body, next_side):
            return None

        distance = self._get_distance_to_corner(self.surface_body, self.surface_side)
        if distance is None or distance > lookahead:
            return None

        return {
            "platform": self.surface_body,
            "from_side": self.surface_side,
            "to_side": next_side,
            "reason": "unsupported_surface",
            "distance": distance,
        }

    def _refresh_surface(self):
        platform = self._find_platform_from_points(self._get_surface_probe_points(self.surface_side), self.surface_side)
        if platform:
            self.surface_body = platform
            self._snap_to_surface(platform, self.surface_side)
            return

        for side in SURFACE_SIDES:
            platform = self._find_platform_from_points(self._get_surface_probe_points(side), side)
            if platform:
                self.surface_side = side
                self.surface_body = platform
                self._snap_to_surface(platform, side)
                return

    def _try_wrap_current_surface(self):
        next_side = self._get_next_side(self.surface_side)
        if not self._has_reached_corner(self.surface_body, self.surface_side):
            return False
        if not self._can_stick_to_platform(self.surface_body, next_side):
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

        distance = self._get_distance_to_corner(platform, side)
        return distance is not None and distance <= 0

    def _get_distance_to_corner(self, platform, side):
        if self._is_ramp(platform):
            return None

        hitbox = self.entity.hitbox
        inset = min(self.corner_inset, max(1, min(hitbox.width, hitbox.height) // 2))

        if side == "bottom":
            if self.clockwise:
                return platform.hitbox.right - inset - hitbox.centerx
            return hitbox.centerx - (platform.hitbox.left + inset)

        if side == "top":
            if self.clockwise:
                return hitbox.centerx - (platform.hitbox.left + inset)
            return platform.hitbox.right - inset - hitbox.centerx

        if side == "left":
            if self.clockwise:
                return platform.hitbox.bottom - inset - hitbox.centery
            return hitbox.centery - (platform.hitbox.top + inset)

        if self.clockwise:
            return hitbox.centery - (platform.hitbox.top + inset)
        return platform.hitbox.bottom - inset - hitbox.centery

    def _find_platform_from_points(self, points, side):
        for point in points:
            platform = self._find_platform_at_point(point, side)
            if platform:
                return platform
        return None

    def _find_platform_at_point(self, point, side):
        platform = self.entity.game_objects.physics.platform_spatial_index.query_point(point)
        if platform is None:
            return None
        if not self._can_stick_to_platform(platform, side):
            return None
        return platform

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
        if not self._can_stick_to_platform(platform, side):
            return False

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

    def _can_stick_to_platform(self, platform, side):
        supports_surface_stick = getattr(platform, "supports_surface_stick", None)
        if supports_surface_stick is None:
            return True
        return supports_surface_stick(self.entity, side)
