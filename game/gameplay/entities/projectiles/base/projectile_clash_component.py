from gameplay.entities.projectiles.base.projectile_clash_results import ProjectileClashResult
from gameplay.entities.shared.components.hit import hit_effects

class ProjectileClashComponent:
    def __init__(self, entity):
        self.entity = entity
        self._active_colliders = set()
        self.result_handlers = {
            ProjectileClashResult.IGNORE: self._handle_ignore,
            ProjectileClashResult.SELF_WINS: self._handle_self_wins,
            ProjectileClashResult.OTHER_WINS: self._handle_other_wins,
            ProjectileClashResult.BOTH_DESTROYED: self._handle_both_destroyed,
        }

    def update(self, dt):
        inactive = []
        for other in self._active_colliders:
            if not getattr(other, 'alive', lambda: False)():
                inactive.append(other)
                continue

            other_hitbox = getattr(other, 'hitbox', None)
            if other_hitbox is None or not self.entity.hitbox.colliderect(other_hitbox):
                inactive.append(other)

        for other in inactive:
            self._active_colliders.discard(other)

    def handle_collision(self, other):
        if not self.can_process(other):
            return ProjectileClashResult.IGNORE

        result = self._resolve_result(other)
        self.result_handlers[result](other)
        return result

    def destroy_from(self, other):
        if not self.can_process(other):
            return False

        self._register_collision(other)
        self._emit_feedback(other, ProjectileClashResult.OTHER_WINS)
        self.entity.on_projectile_clash_lost(other)
        return True

    def reflect_from(self, other, direction, position, team=None, clamp_value=10):
        if not self.can_process(other):
            return False

        self._register_collision(other)
        self._emit_feedback(other, ProjectileClashResult.OTHER_WINS)
        self.entity.on_projectile_reflected(other, direction, position, team=team, clamp_value=clamp_value)
        return True

    def can_process(self, other):
        if other is None or other is self.entity:
            return False

        if not getattr(self.entity, 'alive', lambda: False)():
            return False

        if not getattr(other, 'alive', lambda: False)():
            return False

        return other not in self._active_colliders

    def _resolve_result(self, other):
        if self.entity.team is None or other.team is None:
            result = ProjectileClashResult.IGNORE
        elif self.entity.team == other.team:
            result = ProjectileClashResult.IGNORE
        elif self.entity.team == 'player':
            result = ProjectileClashResult.SELF_WINS
        else:
            result = ProjectileClashResult.OTHER_WINS

        return self.entity.modify_projectile_clash_result(other, result)

    def _register_collision(self, other):
        self._active_colliders.add(other)

    def _handle_ignore(self, other):
        self.entity.on_projectile_clash_ignored(other)

    def _handle_self_wins(self, other):
        self._register_collision(other)
        self._emit_feedback(other, ProjectileClashResult.SELF_WINS)
        other.on_projectile_clash_lost(self.entity)
        self.entity.on_projectile_clash_won(other)

    def _handle_other_wins(self, other):
        self._register_collision(other)
        self._emit_feedback(other, ProjectileClashResult.OTHER_WINS)
        self.entity.on_projectile_clash_lost(other)
        other.on_projectile_clash_won(self.entity)

    def _handle_both_destroyed(self, other):
        self._register_collision(other)
        self._emit_feedback(other, ProjectileClashResult.BOTH_DESTROYED)
        self.entity.on_projectile_clash_lost(other)
        other.on_projectile_clash_lost(self.entity)

    def _emit_feedback(self, other, result):
        effect = self.entity.create_projectile_clash_effect(other, result)
        if not effect:
            return

        effect.attacker = self.entity
        effect.defender = other
        effect.projectile = self.entity

        for callback in effect.defender_callbacks.values():
            callback(effect)

        for callback in effect.attacker_callbacks.values():
            callback(effect)
