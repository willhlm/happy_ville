from gameplay.entities.platforms.base.platform import Platform
from gameplay.entities.shared.components import hit_effects

class CollisionDamage(Platform):#"spikes"
    def __init__(self,pos,size):
        super().__init__(pos,size)
        dmg = 1
        self.effect = hit_effects.HitEffect(damage = dmg)

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self)
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.left_collision(self)
            entity.velocity[0] = 10#knock back

        effect = self.effect.copy()
        effect.attacker = self
        entity.take_hit(effect)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self)
            entity.velocity[1] = 10#knock back

        effect = self.effect.copy()
        effect.attacker = self
        entity.take_hit(effect)
        entity.update_rect_y()

#texture based
