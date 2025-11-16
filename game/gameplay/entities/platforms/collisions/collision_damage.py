from gameplay.entities.platforms.base.platform import Platform
from gameplay.entities.shared.components import hit_effects

class CollisionDamage(Platform):#"spikes"
    def __init__(self,pos,size):
        super().__init__(pos,size)
<<<<<<< HEAD
        #self.dmg = 1
        self.damage = 1
=======
        dmg = 1
        self.effect = hit_effects.HitEffect(damage = dmg)      
>>>>>>> 3403d98d3a7b126c69be4e3699c10199b2b6b8e0

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self)
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.left_collision(self)
<<<<<<< HEAD
            entity.velocity[0] = 10#knock back
        entity.take_dmg(self)
=======
            entity.velocity[0] = 10#knock back        
        
        effect = self.effect.copy()    
        effect.attacker = self
        entity.take_hit(effect)
>>>>>>> 3403d98d3a7b126c69be4e3699c10199b2b6b8e0
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self)
            entity.velocity[1] = 10#knock back
<<<<<<< HEAD
        entity.take_dmg(self)
=======

        effect = self.effect.copy()    
        effect.attacker = self            
        entity.take_hit(effect)
>>>>>>> 3403d98d3a7b126c69be4e3699c10199b2b6b8e0
        entity.update_rect_y()

#texture based
