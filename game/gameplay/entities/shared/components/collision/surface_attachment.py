class NullSurfaceAttachment:
    def __init__(self, entity):
        self.entity = entity

    def is_attached(self):
        return False

    def detach(self):
        return None

    def attach_from_collision(self, collision):
        return False

    def get_surface_motion(self, contact_state=None):
        return None

    def get_stick_velocity(self, speed=1):
        return (0.0, 0.0)

    def post_physics_update(self, dt=None):
        return None


class SurfaceAttachment:
    INWARD_VECTORS = {
        "bottom": (0, 1),
        "top": (0, -1),
        "left": (-1, 0),
        "right": (1, 0),
    }

    def __init__(self, entity):
        self.entity = entity
        self.platform = None
        self.side = None
        self.surface_offset = 0.0

    def is_attached(self):
        return self.platform is not None and self.side is not None

    def detach(self):
        self.platform = None
        self.side = None

    def attach_from_collision(self, collision):
        platform = collision.collider
        side = collision.side
        supports_surface_stick = getattr(platform, "supports_surface_stick", None)
        if supports_surface_stick is not None and not supports_surface_stick(self.entity, side):
            return False

        self.platform = platform
        self.side = side
        self._capture_surface_offset()
        self._snap_to_surface()
        return True

    def get_surface_motion(self, contact_state=None):
        if not self.is_attached():
            return None

        getter = getattr(self.platform, "get_surface_motion", None)
        if getter is None:
            return None

        return getter(self.entity, contact_state=contact_state)

    def get_stick_velocity(self, speed=1):
        if not self.is_attached():
            return (0.0, 0.0)

        inward = self.INWARD_VECTORS[self.side]
        return (inward[0] * speed, inward[1] * speed)

    def post_physics_update(self, dt=None):
        if not self.is_attached():
            return

        if not self.platform.alive():
            self.detach()
            return

        self._capture_surface_offset()
        self._snap_to_surface()

    def _capture_surface_offset(self):
        if not self.is_attached():
            return

        platform_hitbox = self.platform.hitbox

        if self.side in ("bottom", "top"):
            self.surface_offset = self._get_true_hitbox_x(self.entity) - self._get_true_hitbox_x(self.platform)
        else:
            self.surface_offset = self._get_true_hitbox_y(self.entity) - self._get_true_hitbox_y(self.platform)

    def _snap_to_surface(self):
        if not self.is_attached():
            return

        platform_hitbox = self.platform.hitbox
        hitbox = self.entity.hitbox

        if self.side == "bottom":
            max_offset = platform_hitbox.width - hitbox.width
            self.surface_offset = max(0, min(self.surface_offset, max_offset))
            true_hitbox_left = self._get_true_hitbox_x(self.platform) + self.surface_offset
            hitbox.left = round(true_hitbox_left)
            hitbox.bottom = platform_hitbox.top
            self.entity.body.update_rect_x()
            self.entity.true_pos[0] = true_hitbox_left + self._get_rect_hitbox_x_offset(self.entity)
            self.entity.body.update_rect_y()
            return
        elif self.side == "top":
            max_offset = platform_hitbox.width - hitbox.width
            self.surface_offset = max(0, min(self.surface_offset, max_offset))
            true_hitbox_left = self._get_true_hitbox_x(self.platform) + self.surface_offset
            hitbox.left = round(true_hitbox_left)
            hitbox.top = platform_hitbox.bottom
            self.entity.body.update_rect_x()
            self.entity.true_pos[0] = true_hitbox_left + self._get_rect_hitbox_x_offset(self.entity)
            self.entity.body.update_rect_y()
            return
        elif self.side == "left":
            max_offset = platform_hitbox.height - hitbox.height
            self.surface_offset = max(0, min(self.surface_offset, max_offset))
            hitbox.left = platform_hitbox.right
            true_hitbox_top = self._get_true_hitbox_y(self.platform) + self.surface_offset
            hitbox.top = round(true_hitbox_top)
            self.entity.body.update_rect_x()
            self.entity.body.update_rect_y()
            self.entity.true_pos[1] = true_hitbox_top + self._get_rect_hitbox_y_offset(self.entity)
            return
        elif self.side == "right":
            max_offset = platform_hitbox.height - hitbox.height
            self.surface_offset = max(0, min(self.surface_offset, max_offset))
            hitbox.right = platform_hitbox.left
            true_hitbox_top = self._get_true_hitbox_y(self.platform) + self.surface_offset
            hitbox.top = round(true_hitbox_top)
            self.entity.body.update_rect_x()
            self.entity.body.update_rect_y()
            self.entity.true_pos[1] = true_hitbox_top + self._get_rect_hitbox_y_offset(self.entity)

    def _get_true_hitbox_x(self, target):
        return target.true_pos[0] + (target.hitbox.left - target.rect.left)

    def _get_true_hitbox_y(self, target):
        return target.true_pos[1] + (target.hitbox.top - target.rect.top)

    def _get_rect_hitbox_x_offset(self, target):
        return target.rect.left - target.hitbox.left

    def _get_rect_hitbox_y_offset(self, target):
        return target.rect.top - target.hitbox.top
