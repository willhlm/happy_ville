from gameplay.entities.platforms.base.platform import Platform

class CollisionDamage(Platform):#"spikes"
    def __init__(self,pos,size):
        super().__init__(pos,size)
        #self.dmg = 1
        self.damage = 1

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self)
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.left_collision(self)
            entity.velocity[0] = 10#knock back
        entity.take_dmg(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self)
            entity.velocity[1] = 10#knock back
        entity.take_dmg(self)
        entity.update_rect_y()

#texture based
