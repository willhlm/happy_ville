class PlatformMotionRules:
    def __init__(self, entity, resolver):
        self.entity = entity
        self.resolver = resolver

    def get_support_motion(self, block):
        contact_state = getattr(self.entity, 'contact_state', None)
        old_block_hitbox = getattr(block, 'old_hitbox', None)
        delta = getattr(block, 'delta', None)
        if old_block_hitbox is None or delta is None:
            return None

        if delta[0] == 0 and delta[1] == 0:
            return None

        eps = 4
        old_entity_hitbox = getattr(self.entity, 'old_hitbox', self.entity.hitbox)
        previous_support_body = getattr(contact_state, 'previous_support_body', None) if contact_state else None
        support_gap = max(eps, self._get_support_contact_tolerance())
        gap_above_top = old_block_hitbox.top - old_entity_hitbox.bottom
        aligned_on_top = abs(old_entity_hitbox.bottom - old_block_hitbox.top) <= eps
        near_top = 0 <= gap_above_top <= support_gap
        was_on_top = aligned_on_top or near_top or previous_support_body is block
        overlap_x = (
            old_entity_hitbox.right > old_block_hitbox.left and
            old_entity_hitbox.left < old_block_hitbox.right
        )

        if not (was_on_top and overlap_x):
            return None

        return (delta[0], delta[1])

    def _get_support_contact_tolerance(self):
        getter = getattr(self.entity, 'get_support_contact_tolerance', None)
        if getter is None:
            return 1
        return getter()

    def resolve_one_way_up(self, block):
        if self.entity.velocity[1] < 0:
            return False

        old_entity_hitbox = getattr(self.entity, 'old_hitbox', self.entity.hitbox)
        was_above_top = old_entity_hitbox.bottom <= block.hitbox.top + 1
        inside_snap_window = (
            self.entity.hitbox.bottom <=
            block.hitbox.top + self.entity.velocity[1] + abs(self.entity.velocity[0]) + 1
        )
        horizontal_contact = (
            self.entity.hitbox.right > block.hitbox.left and
            self.entity.hitbox.left < block.hitbox.right
        )

        if not horizontal_contact or not was_above_top or not inside_snap_window:
            return False

        self.resolver.push_vertical(block, 'bottom')
        self.resolver.clamp_vertical_velocity()
        return True

    def resolve_right_angle_ramp(self, ramp):
        if ramp.orientation == 0:
            rel_x = ramp.hitbox.right - self.entity.hitbox.left
            other_side = ramp.hitbox.left - self.entity.hitbox.left
            beneath = self.entity.hitbox.bottom - ramp.hitbox.bottom
            ramp.target = -rel_x * ramp.ratio + ramp.hitbox.bottom
            return self._resolve_upward_ramp(ramp, other_side, beneath)

        if ramp.orientation == 1:
            rel_x = self.entity.hitbox.right - ramp.hitbox.left
            other_side = self.entity.hitbox.right - ramp.hitbox.right
            beneath = self.entity.hitbox.bottom - ramp.hitbox.bottom
            ramp.target = -rel_x * ramp.ratio + ramp.hitbox.bottom
            return self._resolve_upward_ramp(ramp, other_side, beneath)

        if ramp.orientation == 2:
            rel_x = ramp.hitbox.right - self.entity.hitbox.left
            ramp.target = rel_x * ramp.ratio + ramp.hitbox.top
            return self._resolve_downward_ramp(ramp)

        rel_x = self.entity.hitbox.right - ramp.hitbox.left
        ramp.target = rel_x * ramp.ratio + ramp.hitbox.top
        return self._resolve_downward_ramp(ramp)

    def request_drop_through(self, colliders, offset=1):
        hitbox = self.entity.hitbox.copy()
        hitbox.bottom += offset

        for candidate in colliders:
            if not hitbox.colliderect(candidate.hitbox):
                continue

            target = candidate.supports_drop_through(self.entity, hitbox)
            if target is None:
                continue
            if self.entity.go_through['drop_through']:
                return False

            self.entity.velocity[1] = offset
            self.entity.go_through['drop_through'] = True
            return True

        return False

    def _resolve_downward_ramp(self, ramp):
        if self.entity.hitbox.top < ramp.target:
            self.resolver.push_ramp(ramp, 'top')
            return True
        return False

    def _resolve_upward_ramp(self, ramp, other_side, beneath):
        if ramp.target > self.entity.hitbox.bottom:
            self.entity.go_through['drop_through'] = False
            return False
        if other_side > 0 or beneath > 0:
            self.entity.go_through['drop_through'] = True
            return False
        if self.entity.go_through['drop_through']:
            return False

        self.resolver.push_ramp(ramp, 'bottom')
        self.resolver.clamp_vertical_velocity()
        return True
