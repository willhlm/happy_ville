from gameplay.entities.platforms.base.platform import Platform
from gameplay.entities.shared.components.hit import hit_effects

class CollisionDamage(Platform):#"spikes"
    def __init__(self,pos,size):
        super().__init__(pos,size)
        dmg = 1
        self.effect = hit_effects.HitEffect(damage = dmg)

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.platform_physics.resolve_side_collision(self, 'right')
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.platform_physics.resolve_side_collision(self, 'left')
            entity.velocity[0] = 10#knock back

        effect = self.effect.copy()
        effect.attacker = self
        entity.take_hit(effect)
        entity.body.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.platform_physics.resolve_vertical_collision(self, 'bottom')
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.platform_physics.resolve_vertical_collision(self, 'top')
            entity.velocity[1] = 10#knock back

        effect = self.effect.copy()
        effect.attacker = self
        entity.take_hit(effect)
        entity.body.update_rect_y()

#texture based
