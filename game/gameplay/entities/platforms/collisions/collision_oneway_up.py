from gameplay.entities.platforms.base.platform import Platform

class CollisionOnewayUp(Platform):
    def __init__(self, pos, size, run_particle = 'dust', go_through = True):
        super().__init__(pos, size, run_particle)
        self.go_through = go_through

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        if entity.velocity[1] < 0: return#going up
        elif type(entity).__name__ == 'Player':
            if self.go_through and entity.flags['go_through']:
                return
        offset = entity.velocity[1] + abs(entity.velocity[0]) + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            entity.down_collision(self)
            entity.limit_y()
            entity.update_rect_y()
