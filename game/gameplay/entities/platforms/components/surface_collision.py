from gameplay.entities.platforms.components.geometry import CollisionSample


class SurfaceCollisionComponent:
    STICKABLE_SIDES = ("bottom", "top", "left", "right")

    def __init__(self, platform, **props):
        self.p = platform
        self.props = props

    def get_floor_samples(self, entity):
        sample = self._build_floor_sample(entity, clamp_floor=True)
        return (sample,) if sample else ()

    def get_ceiling_samples(self, entity):
        sample = self._build_ceiling_sample(entity)
        return (sample,) if sample else ()

    def get_wall_samples(self, entity):
        if self._overlaps_vertically(entity):
            return (
                CollisionSample('right', self.p.hitbox.left, self.p, self, collision_kind='Wall'),
                CollisionSample('left', self.p.hitbox.right, self.p, self, collision_kind='Wall'),
            )
        return ()

    def accepts_floor_contact(self, entity, old_hitbox, current_hitbox, target_y, max_step_up):
        if current_hitbox.bottom < target_y:
            return False
        return old_hitbox.bottom - target_y <= max_step_up

    def accepts_ceiling_contact(self, entity, old_hitbox, current_hitbox, target_y, max_step_down):
        if current_hitbox.top > target_y:
            return False
        return target_y - old_hitbox.top <= max_step_down

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        return None

    def supports_drop_through(self, entity, probe_hitbox):
        return None

    def get_contact_metadata(self, entity, side, axis, collision_kind):
        return {}

    def supports_surface_stick(self, entity, side):
        return side in self.STICKABLE_SIDES

    def _build_floor_sample(self, entity, clamp_floor=False, collision_kind='block'):
        if not self._overlaps_horizontally(entity):
            return None
        return CollisionSample('bottom', self.p.hitbox.top, self.p, self, collision_kind=collision_kind, clamp_floor=clamp_floor)

    def _build_ceiling_sample(self, entity, collision_kind='block'):
        if not self._overlaps_horizontally(entity):
            return None
        return CollisionSample('top', self.p.hitbox.bottom, self.p, self, collision_kind=collision_kind)

    def _overlaps_horizontally(self, entity, hitbox=None):
        hitbox = hitbox or entity.hitbox
        return (
            hitbox.right > self.p.hitbox.left and
            hitbox.left < self.p.hitbox.right
        )

    def _overlaps_vertically(self, entity, hitbox=None):
        hitbox = hitbox or entity.hitbox
        return (
            hitbox.bottom > self.p.hitbox.top and
            hitbox.top < self.p.hitbox.bottom
        )


class SolidSurfaceCollisionComponent(SurfaceCollisionComponent):
    pass


class OneWayUpSurfaceCollisionComponent(SurfaceCollisionComponent):
    STICKABLE_SIDES = ("bottom",)

    def get_ceiling_samples(self, entity):
        return ()

    def get_wall_samples(self, entity):
        return ()

    def accepts_floor_contact(self, entity, old_hitbox, current_hitbox, target_y, max_step_up):
        if entity.go_through.get('drop_through', False):
            return False
        if entity.velocity[1] < 0:
            return False
        if current_hitbox.bottom < target_y:
            return False
        return old_hitbox.bottom <= target_y + 1

    def supports_drop_through(self, entity, probe_hitbox):
        if not self._overlaps_horizontally(entity, hitbox=probe_hitbox):
            return None
        if probe_hitbox.bottom < self.p.hitbox.top:
            return None
        return self.p.hitbox.top


class RightAngleSurfaceCollisionComponent(SurfaceCollisionComponent):
    def get_floor_samples(self, entity):
        if self.p.orientation not in (0, 1):
            return ()

        target = self._get_floor_target(entity.hitbox)
        if target is None:
            return ()

        return (CollisionSample('bottom', target, self.p, self, clamp_floor=True),)

    def get_ceiling_samples(self, entity):
        if self.p.orientation not in (2, 3):
            return ()

        target = self._get_ceiling_target(entity.hitbox)
        if target is None:
            return ()

        return (CollisionSample('top', target, self.p, self),)

    def get_wall_samples(self, entity):
        return ()

    def accepts_floor_contact(self, entity, old_hitbox, current_hitbox, target_y, max_step_up):
        if self.p.go_through and self._should_latch_drop_through(
            old_hitbox,
            current_hitbox,
            target_y,
            max_step_up,
        ):
            entity.go_through['drop_through'] = True
            return False
        if self.p.go_through and self.p.entity_is_dropping(entity):
            return False
        if current_hitbox.bottom < target_y:
            if target_y - old_hitbox.bottom > 1:
                return False
            return target_y - current_hitbox.bottom <= max_step_up
        return super().accepts_floor_contact(entity, old_hitbox, current_hitbox, target_y, max_step_up)

    def supports_drop_through(self, entity, probe_hitbox):
        if self.p.orientation not in (0, 1) or not self.p.go_through:
            return None

        target = self._get_floor_target(probe_hitbox)
        if target is None or target > probe_hitbox.bottom:
            return None
        return target

    def supports_surface_stick(self, entity, side):
        if self.p.orientation in (0, 1):
            return side == "bottom"
        if self.p.orientation in (2, 3):
            return side == "top"
        return False

    def _get_floor_target(self, hitbox):
        if self.p.orientation == 0:
            left = max(hitbox.left, self.p.hitbox.left)
            if left >= self.p.hitbox.right or hitbox.right <= self.p.hitbox.left:
                return None
            rel_x = self.p.hitbox.right - left
            return -rel_x * self.p.ratio + self.p.hitbox.bottom

        if self.p.orientation == 1:
            right = min(hitbox.right, self.p.hitbox.right)
            if right <= self.p.hitbox.left or hitbox.left >= self.p.hitbox.right:
                return None
            rel_x = right - self.p.hitbox.left
            return -rel_x * self.p.ratio + self.p.hitbox.bottom

        return None

    def _get_ceiling_target(self, hitbox):
        if self.p.orientation == 2:
            left = max(hitbox.left, self.p.hitbox.left)
            if left >= self.p.hitbox.right or hitbox.right <= self.p.hitbox.left:
                return None
            rel_x = self.p.hitbox.right - left
            return rel_x * self.p.ratio + self.p.hitbox.top

        if self.p.orientation == 3:
            right = min(hitbox.right, self.p.hitbox.right)
            if right <= self.p.hitbox.left or hitbox.left >= self.p.hitbox.right:
                return None
            rel_x = right - self.p.hitbox.left
            return rel_x * self.p.ratio + self.p.hitbox.top

        return None

    def _should_latch_drop_through(self, old_hitbox, current_hitbox, target_y, max_step_up):
        if self.p.orientation == 0:
            entered_from_blocked_side = (
                old_hitbox.right <= self.p.hitbox.left and
                current_hitbox.right > self.p.hitbox.left
            )
        elif self.p.orientation == 1:
            entered_from_blocked_side = (
                old_hitbox.left >= self.p.hitbox.right and
                current_hitbox.left < self.p.hitbox.right
            )
        else:
            return False

        entered_from_below = (
            old_hitbox.top >= self.p.hitbox.bottom and
            current_hitbox.top < self.p.hitbox.bottom
        )
        well_below_surface = current_hitbox.bottom > target_y + max_step_up
        return entered_from_below or (entered_from_blocked_side and well_below_surface)
