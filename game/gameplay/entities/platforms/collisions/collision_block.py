from gameplay.entities.platforms.base.platform import Platform

class CollisionBlock(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos, size, run_particle)

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.platform_physics.resolve_side_collision(self, 'right')
        else:#going to the leftx
            entity.platform_physics.resolve_side_collision(self, 'left')
        entity.body.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            entity.platform_physics.resolve_vertical_collision(self, 'bottom')
            entity.platform_physics.limit_y()
        else:#going up
            entity.platform_physics.resolve_vertical_collision(self, 'top')
        entity.body.update_rect_y()
