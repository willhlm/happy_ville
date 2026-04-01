from engine import constants as C


class PlatformPhysics:
    def __init__(self, entity):
        self.entity = entity
        self.enabled = True

    def can_collide(self):
        return self.enabled

    def is_crushed(self, block, side):
        if not self._is_pushing_towards_entity(block, side):
            return False
        if not self._was_on_crushing_side(block, side):
            return False

        projected = self.entity.hitbox.copy()
        if side == 'bottom':
            projected.bottom = block.hitbox.top
        elif side == 'top':
            projected.top = block.hitbox.bottom
        elif side == 'right':
            projected.right = block.hitbox.left
        else:
            projected.left = block.hitbox.right

        for platform in self.entity.game_objects.platforms:
            if platform is block or not hasattr(platform, 'hitbox'):
                continue
            if self._is_blocked_on_opposite_side(projected, platform.hitbox, side):
                return True
        return False

    def handle_crush(self, block):
        self.entity.on_crush(block)

    def _is_pushing_towards_entity(self, block, side):
        dx, dy = getattr(block, 'delta', [0, 0])
        if side == 'bottom':
            return dy < 0
        if side == 'top':
            return dy > 0
        if side == 'right':
            return dx < 0
        return dx > 0

    def _was_on_crushing_side(self, block, side):
        eps = 1
        old_block_hitbox = getattr(block, 'old_hitbox', block.hitbox)
        old_entity_hitbox = getattr(self.entity, 'old_hitbox', self.entity.hitbox)

        if side == 'top':
            return (
                old_block_hitbox.centery <= old_entity_hitbox.centery and
                old_block_hitbox.top <= old_entity_hitbox.top + eps
            )
        if side == 'bottom':
            return (
                old_block_hitbox.centery >= old_entity_hitbox.centery and
                old_block_hitbox.bottom >= old_entity_hitbox.bottom - eps
            )
        if side == 'right':
            return (
                old_block_hitbox.centerx >= old_entity_hitbox.centerx and
                old_block_hitbox.right >= old_entity_hitbox.right - eps
            )
        return (
            old_block_hitbox.centerx <= old_entity_hitbox.centerx and
            old_block_hitbox.left <= old_entity_hitbox.left + eps
        )

    def _is_blocked_on_opposite_side(self, projected, blocker, side):
        overlap_x = projected.right > blocker.left and projected.left < blocker.right
        overlap_y = projected.bottom > blocker.top and projected.top < blocker.bottom

        if side == 'top':
            return overlap_x and projected.bottom >= blocker.top
        if side == 'bottom':
            return overlap_x and projected.top <= blocker.bottom
        if side == 'right':
            return overlap_y and projected.left <= blocker.right
        return overlap_y and projected.right >= blocker.left

    def resolve_ramp_collision(self, ramp, side):
        if side == 'top':
            self.entity.hitbox.top = ramp.target
            self.entity.collision_types['top'] = True
            self.entity.velocity[1] = 2
            self.entity.velocity[0] = 0
        else:
            self.entity.hitbox.bottom = ramp.target
            self.entity.collision_types['bottom'] = True
            self.entity.velocity[1] = C.max_vel[1] + 10

        self.entity.on_ramp_collision(side, ramp)

    def resolve_side_collision(self, block, side, collision_type = 'Wall'):
        if side == 'right':
            self.entity.hitbox.right = block.hitbox.left
            self.entity.collision_types['right'] = True
        else:
            self.entity.hitbox.left = block.hitbox.right
            self.entity.collision_types['left'] = True

        self.entity.on_platform_side_collision(side, block, collision_type)

    def resolve_vertical_collision(self, block, side):
        if side == 'bottom':
            self.entity.hitbox.bottom = block.hitbox.top
            self.entity.collision_types['bottom'] = True
        else:
            self.entity.hitbox.top = block.hitbox.bottom
            self.entity.collision_types['top'] = True

        self.entity.on_platform_vertical_collision(side, block)

    def limit_y(self):
        self.entity.on_limit_y()
