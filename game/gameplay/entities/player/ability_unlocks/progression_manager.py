from .ability_manager import AbilityManager
from .traversal_unlock_manager import TraversalUnlockManager


class PlayerProgressionManager:
    def __init__(self, entity):
        self.entity = entity
        self.abilities = AbilityManager(entity)
        self.traversal = TraversalUnlockManager(entity)

    def _is_ability_key(self, progress_key):
        return progress_key in self.abilities.abilities

    def _is_traversal_key(self, progress_key):
        return progress_key in self.traversal.BUNDLES

    def is_unlocked(self, progress_key):
        if self._is_ability_key(progress_key):
            return self.abilities.is_unlocked(progress_key)
        if self._is_traversal_key(progress_key):
            return self.traversal.has_unlock(progress_key)
        raise KeyError(f"Unknown progression key: {progress_key}")

    def unlock(self, progress_key):
        if self._is_ability_key(progress_key):
            return self.abilities.unlock(progress_key)
        if self._is_traversal_key(progress_key):
            self.traversal.unlock(progress_key)
            return None
        raise KeyError(f"Unknown progression key: {progress_key}")

    def can_upgrade(self, progress_key):
        if self._is_ability_key(progress_key):
            return self.abilities.can_upgrade(progress_key)
        if self._is_traversal_key(progress_key):
            return False
        raise KeyError(f"Unknown progression key: {progress_key}")

    def upgrade(self, progress_key):
        if self._is_ability_key(progress_key):
            return self.abilities.upgrade(progress_key)
        raise KeyError(f"Unknown progression key: {progress_key}")

    def get_current_description(self, progress_key):
        if self._is_ability_key(progress_key):
            return self.abilities.get_current_description(progress_key)
        if self._is_traversal_key(progress_key):
            return None
        raise KeyError(f"Unknown progression key: {progress_key}")

    def get_next_upgrade_description(self, progress_key):
        if self._is_ability_key(progress_key):
            return self.abilities.get_next_upgrade_description(progress_key)
        if self._is_traversal_key(progress_key):
            return None
        raise KeyError(f"Unknown progression key: {progress_key}")

    def get_progress_key_for_boss(self, boss_id):
        for ability in self.abilities.abilities.values():
            if ability.unlock_boss_id == boss_id:
                return ability.id
        return None

    def get_preview_sprite(self, progress_key):
        if self._is_ability_key(progress_key):
            return f'{self.abilities.get(progress_key).state_name}_main'
        if self._is_traversal_key(progress_key):
            preview_sprites = {
                'dash': 'dash_ground_main',
                'air_dash': 'air_dash_main',
                'climbing_gear': 'wall_glide_main',
            }
            return preview_sprites.get(progress_key)
        raise KeyError(f"Unknown progression key: {progress_key}")
