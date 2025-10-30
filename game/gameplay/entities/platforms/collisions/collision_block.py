from gameplay.entities.platforms.base.platform import Platform

class CollisionBlock(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos, size, run_particle)

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):    
        if entity.velocity[1] > 0:#going down
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()
