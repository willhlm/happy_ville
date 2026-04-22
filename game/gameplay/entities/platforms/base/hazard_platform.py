from gameplay.entities.platforms.base.solid_platform import SolidPlatform
from gameplay.entities.shared.components.hit import hit_effects


class HazardPlatform(SolidPlatform):
    def __init__(self, pos, size=(16, 16), damage=1, knockback_x=10, knockback_y=10, run_particle='dust'):
        super().__init__(pos, size=size, run_particle=run_particle)
        self.effect = hit_effects.HitEffect(damage=damage)
        self.knockback_x = knockback_x
        self.knockback_y = knockback_y

    def _apply_damage(self, entity):
        effect = self.effect.copy()
        effect.attacker = self
        entity.take_hit(effect)

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        if axis == 'x':
            if side == 'right':
                entity.velocity[0] = -self.knockback_x
            elif side == 'left':
                entity.velocity[0] = self.knockback_x
        elif axis == 'y':
            if side == 'bottom':
                entity.velocity[1] = -self.knockback_y
            elif side == 'top':
                entity.velocity[1] = self.knockback_y

        self._apply_damage(entity)
