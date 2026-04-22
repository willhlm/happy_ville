class PlatformCrushResolver:
    def __init__(self, entity):
        self.entity = entity

    def is_crushed(self, block, side):
        pushing = self._is_pushing_towards_entity(block, side)
        was_on_side = self._was_on_crushing_side(block, side)
        if not pushing or not was_on_side:
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

        blocker = self._find_opposite_blocker(projected, block, side)
        return blocker is not None

    def handle_crush(self, block, side=None):
        crush_handler = getattr(block, 'handle_entity_crush', None)
        if crush_handler is not None:
            return crush_handler(self.entity, side=side)

        self.entity.on_crush(block)
        return True

    def has_opposite_blocker(self, block, side, projected=None):
        projected = projected or self.entity.hitbox
        return self._find_opposite_blocker(projected, block, side) is not None

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
            return old_entity_hitbox.top >= old_block_hitbox.bottom - eps
        if side == 'bottom':
            return old_entity_hitbox.bottom <= old_block_hitbox.top + eps
        if side == 'right':
            return old_entity_hitbox.right <= old_block_hitbox.left + eps
        return old_entity_hitbox.left >= old_block_hitbox.right - eps

    def _find_opposite_blocker(self, projected, moving_block, side):
        for platform in self.entity.game_objects.platforms:
            if platform is moving_block or not hasattr(platform, 'hitbox'):
                continue
            if self._is_blocked_on_opposite_side(projected, platform.hitbox, side):
                return platform
        return None

    @staticmethod
    def _is_blocked_on_opposite_side(projected, blocker, side):
        overlap_x = projected.right > blocker.left and projected.left < blocker.right
        overlap_y = projected.bottom > blocker.top and projected.top < blocker.bottom

        if side == 'top':
            return overlap_x and projected.bottom > blocker.top and projected.top < blocker.top
        if side == 'bottom':
            return overlap_x and projected.top < blocker.bottom and projected.bottom > blocker.bottom
        if side == 'right':
            return overlap_y and projected.left < blocker.right and projected.right > blocker.right
        return overlap_y and projected.right > blocker.left and projected.left < blocker.left
