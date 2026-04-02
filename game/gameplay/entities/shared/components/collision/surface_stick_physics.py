class SurfaceStickPhysics:
    SURFACE_NORMALS = {
        'bottom': [0, -1],
        'left': [1, 0],
        'top': [0, 1],
        'right': [-1, 0],
    }

    SURFACE_ANGLES = {
        'bottom': 0,
        'left': 90,
        'top': 180,
        'right': -90,
    }

    def __init__(self, entity, speed, stick_speed=1.5, probe_distance=2, corner_inset=3, initial_side='bottom'):
        self.entity = entity
        self.speed = speed
        self.stick_speed = stick_speed
        self.probe_distance = probe_distance
        self.corner_inset = corner_inset

        self.surface_side = initial_side
        self.surface_normal = self.SURFACE_NORMALS[initial_side][:]
        self.pending_contacts = []
        self.preferred_surface_side = initial_side

        self._sync_visuals()

    def update_velocity(self):
        self._sync_surface_from_contacts()
        self._turn_corner_if_needed()

        tangent = self.get_tangent()
        inward = [-self.surface_normal[0], -self.surface_normal[1]]

        self.entity.velocity[0] = tangent[0] * self.speed + inward[0] * self.stick_speed
        self.entity.velocity[1] = tangent[1] * self.speed + inward[1] * self.stick_speed
        self._sync_visuals()

    def register_contact(self, side, block=None):
        self.pending_contacts.append((side, block))

    def get_tangent(self):
        direction = getattr(self.entity, 'clockwise', 1)
        return [self.surface_normal[1] * direction, self.surface_normal[0] * direction]

    def _sync_surface_from_contacts(self):
        if not self.pending_contacts:
            if self.surface_side != 'bottom':
                self.entity.standing_platform = None
            return

        sides = [side for side, _ in self.pending_contacts]

        if self.surface_side in sides:
            chosen_side = self.surface_side
        elif self.preferred_surface_side in sides:
            chosen_side = self.preferred_surface_side
        elif len(set(sides)) == 1:
            chosen_side = sides[0]
        else:
            chosen_side = self.surface_side

        chosen_block = None
        for side, block in self.pending_contacts:
            if side == chosen_side:
                chosen_block = block
                break

        self.pending_contacts.clear()
        self._set_surface(chosen_side, chosen_block)
        self.preferred_surface_side = chosen_side

    def _turn_corner_if_needed(self):
        if self._has_surface_ahead():
            return

        next_normal = self._get_corner_normal()
        next_side = self._get_side_from_normal(next_normal)
        if self._has_corner_surface():
            self._set_surface(next_side)
            self.preferred_surface_side = next_side
            return

        self.entity.clockwise *= -1
        self.preferred_surface_side = self.surface_side
        self._sync_visuals()

    def _has_surface_ahead(self):
        tangent = self.get_tangent()
        inward = [-self.surface_normal[0], -self.surface_normal[1]]
        probe = self._get_current_surface_probe(tangent, inward)
        return self._is_solid_point(probe)

    def _has_corner_surface(self):
        tangent = self.get_tangent()
        inward = [-self.surface_normal[0], -self.surface_normal[1]]
        return any(self._is_solid_point(probe) for probe in self._get_corner_probes(tangent, inward))

    def _get_probe_point(self, tangent_scale, inward_scale, tangent, inward):
        centerx, centery = self.entity.hitbox.center
        tangent_scale = max(0, tangent_scale)
        inward_scale = max(0, inward_scale)

        return (
            round(centerx + tangent[0] * tangent_scale + inward[0] * inward_scale),
            round(centery + tangent[1] * tangent_scale + inward[1] * inward_scale),
        )

    def _get_current_surface_probe(self, tangent, inward):
        leading_corner = self._get_leading_corner(tangent, inward)
        return (
            round(leading_corner[0] - tangent[0] * self.corner_inset + inward[0] * self.probe_distance),
            round(leading_corner[1] - tangent[1] * self.corner_inset + inward[1] * self.probe_distance),
        )

    def _get_corner_probes(self, tangent, inward):
        leading_corner = self._get_leading_corner(tangent, inward)
        next_normal = self._get_corner_normal()
        next_inward = [-next_normal[0], -next_normal[1]]

        probes = [
            (
                round(leading_corner[0] + next_inward[0] * self.probe_distance),
                round(leading_corner[1] + next_inward[1] * self.probe_distance),
            ),
            (
                round(leading_corner[0] + next_inward[0] * self.probe_distance + inward[0] * self.probe_distance),
                round(leading_corner[1] + next_inward[1] * self.probe_distance + inward[1] * self.probe_distance),
            ),
            (
                round(leading_corner[0] + next_inward[0] * (self.probe_distance + self.corner_inset)),
                round(leading_corner[1] + next_inward[1] * (self.probe_distance + self.corner_inset)),
            ),
        ]
        return probes

    def _get_leading_corner(self, tangent, inward):
        centerx, centery = self.entity.hitbox.center
        return (
            centerx + tangent[0] * self._axis_extent(tangent) + inward[0] * self._axis_extent(inward),
            centery + tangent[1] * self._axis_extent(tangent) + inward[1] * self._axis_extent(inward),
        )

    def _is_solid_point(self, point):
        for group_name in ('platforms', 'platforms_ramps'):
            group = getattr(self.entity.game_objects, group_name, [])
            for platform in group:
                hitbox = getattr(platform, 'hitbox', None)
                if hitbox and hitbox.collidepoint(point):
                    return True
        return False

    def _get_corner_normal(self):
        nx, ny = self.surface_normal
        if self.entity.clockwise > 0:
            return [-ny, nx]
        return [ny, -nx]

    def _set_surface(self, side, block=None):
        self.surface_side = side
        self.surface_normal = self.SURFACE_NORMALS[side][:]
        self.entity.angle = self.SURFACE_ANGLES[side]

        if side == 'bottom':
            self.entity.standing_platform = block
        else:
            self.entity.standing_platform = None

    def _sync_visuals(self):
        tangent = self.get_tangent()
        if tangent[0] != 0:
            self.entity.dir[0] = 1 if tangent[0] > 0 else -1
        self.entity.angle = self.SURFACE_ANGLES[self.surface_side]

    def _axis_extent(self, direction):
        if direction[0] != 0:
            return self.entity.hitbox.width * 0.5
        return self.entity.hitbox.height * 0.5

    def _get_side_from_normal(self, normal):
        for side, side_normal in self.SURFACE_NORMALS.items():
            if side_normal[0] == normal[0] and side_normal[1] == normal[1]:
                return side
        return self.surface_side
