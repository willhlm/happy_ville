import math

from engine import constants as C


class PlatformContactResolver:
    def __init__(self, entity):
        self.entity = entity

    def resolve_horizontal(self, block, collision_type='Wall'):
        side = self._get_horizontal_collision_side(block)
        if side is None:
            return None

        self.push_horizontal(block, side, collision_type=collision_type)
        return side

    def resolve_vertical(self, block, clamp_floor=False):
        side = self._get_vertical_collision_side(block)
        if side is None:
            return None

        self.push_vertical(block, side)
        if side == 'bottom' and clamp_floor:
            self.clamp_vertical_velocity()
        return side

    def resolve_horizontal_strict(self, block, collision_type='Wall', eps=1):
        side = self._get_horizontal_collision_side_strict(block, eps=eps)
        if side is None:
            return None

        self.push_horizontal(block, side, collision_type=collision_type)
        return side

    def resolve_vertical_strict(self, block, clamp_floor=False, eps=1):
        side = self._get_vertical_collision_side_strict(block, eps=eps)
        if side is None:
            return None

        self.push_vertical(block, side)
        if side == 'bottom' and clamp_floor:
            self.clamp_vertical_velocity()
        return side

    def resolve_polygon(self, polygon, overlap, axis):
        direction = (
            self.entity.hitbox.centerx - polygon.rect.centerx,
            self.entity.hitbox.centery - polygon.rect.centery,
        )
        sign = 1 if self._dot(direction, axis) > 0 else -1
        move_x = axis[0] * overlap * sign
        move_y = axis[1] * overlap * sign

        self.entity.hitbox.x += move_x
        self.entity.hitbox.y += move_y

        side = self._polygon_collision_side(move_x, move_y)
        collision = self._record_contact(
            side,
            polygon,
            axis='y' if side in ('top', 'bottom') else 'x',
            collision_kind='polygon',
        )
        if collision is not None:
            collision.normal = self._normalize((-axis[0] * sign, -axis[1] * sign))

        self.entity.body.update_rect_x()
        self.entity.body.update_rect_y()
        return side

    def push_ramp(self, ramp, side):
        if side == 'top':
            self.entity.hitbox.top = ramp.target
            self.entity.velocity[1] = 2
            self.entity.velocity[0] = 0
        else:
            self.entity.hitbox.bottom = ramp.target
            self.entity.velocity[1] = C.max_vel[1] + 10

        self._record_contact(side, ramp, axis='y', collision_kind='ramp')
        self.entity.body.update_rect_y()

    def push_vertical_sample(self, sample):
        if sample.side == 'bottom':
            self.entity.hitbox.bottom = sample.position
        else:
            self.entity.hitbox.top = sample.position

        self._record_contact(sample.side, sample.collider, axis='y', collision_kind=sample.collision_kind)
        self.entity.body.update_rect_y()

    def push_horizontal_sample(self, sample):
        if sample.side == 'right':
            self.entity.hitbox.right = sample.position
        else:
            self.entity.hitbox.left = sample.position

        self._record_contact(sample.side, sample.collider, axis='x', collision_kind=sample.collision_kind)
        self.entity.body.update_rect_x()

    def push_horizontal(self, block, side, collision_type='Wall'):
        if side == 'right':
            self.entity.hitbox.right = block.hitbox.left
        else:
            self.entity.hitbox.left = block.hitbox.right

        self._record_contact(side, block, axis='x', collision_kind=collision_type)
        self.entity.body.update_rect_x()

    def push_vertical(self, block, side):
        if side == 'bottom':
            self.entity.hitbox.bottom = block.hitbox.top
        else:
            self.entity.hitbox.top = block.hitbox.bottom

        self._record_contact(side, block, axis='y')
        self.entity.body.update_rect_y()

    def clamp_vertical_velocity(self):
        self.entity.apply_ground_snap_velocity()

    def _record_contact(self, side, block, axis, collision_kind='block'):
        contact_state = getattr(self.entity, 'contact_state', None)
        if contact_state is None:
            return None

        metadata_getter = getattr(block, 'get_contact_metadata', None)
        metadata = metadata_getter(self.entity, side, axis, collision_kind) if metadata_getter else None
        return contact_state.record(side, block, axis, collision_kind, metadata=metadata)

    def _get_horizontal_collision_side(self, block, eps=1):
        side = self._get_horizontal_collision_side_strict(block, eps=eps)
        if side is not None:
            return side

        if self.entity.velocity[0] > 0:
            return 'right'
        if self.entity.velocity[0] < 0:
            return 'left'
        return None

    def _get_horizontal_collision_side_strict(self, block, eps=1):
        old_block_hitbox = getattr(block, 'old_hitbox', block.hitbox)
        old_entity_hitbox = getattr(self.entity, 'old_hitbox', self.entity.hitbox)

        hit_from_left = (
            self.entity.hitbox.right >= block.hitbox.left and
            old_entity_hitbox.right <= old_block_hitbox.left + eps
        )
        hit_from_right = (
            self.entity.hitbox.left <= block.hitbox.right and
            old_entity_hitbox.left >= old_block_hitbox.right - eps
        )

        if hit_from_left:
            return 'right'
        if hit_from_right:
            return 'left'
        return None

    def _get_vertical_collision_side(self, block, eps=1):
        side = self._get_vertical_collision_side_strict(block, eps=eps)
        if side is not None:
            return side

        if self.entity.velocity[1] > 0:
            return 'bottom'
        if self.entity.velocity[1] < 0:
            return 'top'
        return None

    def _get_vertical_collision_side_strict(self, block, eps=1):
        old_block_hitbox = getattr(block, 'old_hitbox', block.hitbox)
        old_entity_hitbox = getattr(self.entity, 'old_hitbox', self.entity.hitbox)

        landed_from_above = (
            self.entity.hitbox.bottom >= block.hitbox.top and
            old_entity_hitbox.bottom <= old_block_hitbox.top + eps
        )
        hit_from_below = (
            self.entity.hitbox.top <= block.hitbox.bottom and
            old_entity_hitbox.top >= old_block_hitbox.bottom - eps
        )

        if landed_from_above:
            return 'bottom'
        if hit_from_below:
            return 'top'
        return None

    @staticmethod
    def _dot(a, b):
        return a[0] * b[0] + a[1] * b[1]

    @staticmethod
    def _normalize(vector):
        length = math.hypot(vector[0], vector[1])
        if length == 0:
            return (0, 0)
        return (vector[0] / length, vector[1] / length)

    @staticmethod
    def _polygon_collision_side(move_x, move_y):
        if abs(move_y) >= abs(move_x):
            return 'bottom' if move_y < 0 else 'top'
        return 'right' if move_x < 0 else 'left'
