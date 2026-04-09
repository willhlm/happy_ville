class ContactEffect:
    def apply(self, entity):
        return None

    @classmethod
    def from_mapping(cls, mapping):
        return cls()


class MotionResult:
    def __init__(self):
        self.reset()

    def reset(self):
        self.requested_motion = (0.0, 0.0)
        self.travel = (0.0, 0.0)
        self.remainder = (0.0, 0.0)
        self.start_position = (0, 0)
        self.end_position = (0, 0)
        self.had_collision = False


class SlideCollision:
    SIDE_NORMALS = {
        'bottom': (0, -1),
        'top': (0, 1),
        'left': (1, 0),
        'right': (-1, 0),
    }

    def __init__(self, side, collider, axis, collision_kind='block', metadata=None):
        self.side = side
        self.collider = collider
        self.axis = axis
        self.collision_kind = collision_kind
        self.normal = self.SIDE_NORMALS[side]
        if isinstance(metadata, ContactEffect):
            self.contact_effect = metadata
        else:
            self.contact_effect = ContactEffect.from_mapping(metadata)
        self.metadata = self.contact_effect


class ContactState:
    def __init__(self):
        self.collisions = []
        self._seen = set()
        self.motion_result = MotionResult()
        self.was_on_floor = False
        self.was_on_wall = False
        self.was_on_ceiling = False
        self.previous_surface_normal = None
        self.previous_surface_body = None
        self.previous_support_body = None
        self.support_velocity = (0.0, 0.0)
        self.previous_support_velocity = (0.0, 0.0)
        self.applied_support_motion = (0.0, 0.0)
        self.previous_applied_support_motion = (0.0, 0.0)
        self.reset()

    def reset(self):
        self.collisions.clear()
        self._seen.clear()
        self.floor_collision = None
        self.ceiling_collision = None
        self.wall_collisions = []
        self.collision_types = {'top': False, 'bottom': False, 'left': False, 'right': False}
        self.surface_collision = None
        self.surface_body = None
        self.support_body = None
        self.support_velocity = (0.0, 0.0)
        self.applied_support_motion = (0.0, 0.0)
        self.motion_result.reset()

    def begin_step(self, requested_motion, start_hitbox):
        self.was_on_floor = self.is_on_floor()
        self.was_on_wall = self.is_on_wall()
        self.was_on_ceiling = self.is_on_ceiling()
        self.previous_surface_normal = self.get_surface_normal()
        self.previous_surface_body = self.surface_body
        self.previous_support_body = self.support_body
        self.previous_support_velocity = self.support_velocity
        self.previous_applied_support_motion = self.applied_support_motion
        self.reset()
        self.motion_result.requested_motion = (requested_motion[0], requested_motion[1])
        self.motion_result.start_position = (start_hitbox.left, start_hitbox.top)

    def record(self, side, collider, axis, collision_kind='block', metadata=None):
        key = (id(collider), side, axis, collision_kind)
        if key in self._seen:
            return None

        self._seen.add(key)
        collision = SlideCollision(side, collider, axis, collision_kind, metadata=metadata)
        self.collisions.append(collision)
        self.collision_types[side] = True

        if side == 'bottom':
            self.floor_collision = self.floor_collision or collision
        elif side == 'top':
            self.ceiling_collision = self.ceiling_collision or collision
        else:
            self.wall_collisions.append(collision)

        return collision

    def finalize(self):
        if self.floor_collision:
            self.surface_collision = self.floor_collision
        elif self.wall_collisions:
            self.surface_collision = self.wall_collisions[0]
        elif self.ceiling_collision:
            self.surface_collision = self.ceiling_collision
        else:
            self.surface_collision = None

        self.surface_body = self.surface_collision.collider if self.surface_collision else None
        self.support_body = self.floor_collision.collider if self.floor_collision else None
        if self.support_body is not None:
            self.support_velocity = tuple(getattr(self.support_body, 'velocity', (0.0, 0.0)))
        self.motion_result.had_collision = bool(self.collisions)

    def complete_motion(self, end_hitbox):
        end_position = (end_hitbox.left, end_hitbox.top)
        self.motion_result.end_position = end_position

        travel = (
            end_position[0] - self.motion_result.start_position[0],
            end_position[1] - self.motion_result.start_position[1],
        )
        self.motion_result.travel = travel
        self.motion_result.remainder = (
            self.motion_result.requested_motion[0] - travel[0],
            self.motion_result.requested_motion[1] - travel[1],
        )

    def iter_sides(self):
        for collision in self.collisions:
            yield collision.side

    def has_side(self, side):
        return self.collision_types.get(side, False)

    def get_collisions_for_side(self, side):
        return [collision for collision in self.collisions if collision.side == side]

    def has_collision_kind(self, collision_kind, side=None):
        for collision in self.collisions:
            if side is not None and collision.side != side:
                continue
            if collision.collision_kind == collision_kind:
                return True
        return False

    def get_surface_normal(self):
        if not self.surface_collision:
            return None
        return self.surface_collision.normal

    def get_floor_normal(self):
        if not self.floor_collision:
            return None
        return self.floor_collision.normal

    def get_wall_normal(self):
        if not self.wall_collisions:
            return None
        return self.wall_collisions[0].normal

    def get_slide_collision_count(self):
        return len(self.collisions)

    def get_slide_collision(self, index):
        if index < 0 or index >= len(self.collisions):
            return None
        return self.collisions[index]

    def get_real_velocity(self, dt):
        if dt == 0:
            return (0.0, 0.0)
        return (
            self.motion_result.travel[0] / dt,
            self.motion_result.travel[1] / dt,
        )

    def is_on_floor(self):
        return self.floor_collision is not None

    def is_on_wall(self):
        return bool(self.wall_collisions)

    def is_on_ceiling(self):
        return self.ceiling_collision is not None
