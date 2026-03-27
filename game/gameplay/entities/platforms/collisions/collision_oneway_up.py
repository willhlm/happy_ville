from gameplay.entities.platforms.base.platform import Platform

class CollisionOnewayUp(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos, size, run_particle)

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        if entity.velocity[1] < 0:
            return#going up

        old_hitbox = getattr(entity, 'old_hitbox', entity.hitbox)
        crossed_top = old_hitbox.bottom <= self.hitbox.top and entity.hitbox.bottom >= self.hitbox.top
        inside_snap_window = entity.hitbox.bottom <= self.hitbox.top + entity.velocity[1] + abs(entity.velocity[0]) + 1
        horizontal_contact = (
            entity.hitbox.right >= self.hitbox.left and
            entity.hitbox.left <= self.hitbox.right
        )

        if horizontal_contact and (crossed_top or inside_snap_window):
            entity.down_collision(self)
            entity.limit_y()
            entity.update_rect_y()
