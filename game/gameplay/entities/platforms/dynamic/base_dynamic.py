from gameplay.entities.platforms.texture.base_texture import BaseTexture
from gameplay.entities.shared.components.body.entity_body import EntityBody

class BaseDynamic(BaseTexture):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.body = EntityBody(self, anchor='topleft')
        self.old_hitbox = self.hitbox.copy()
        self.velocity = [0,0]
        self.delta = [0,0]

    def update(self, dt):
        super().update(dt)
        self.old_hitbox = self.hitbox.copy()#save old position before moving
        self.update_vel(dt)
        self.body.update_true_pos_x(dt)#used be int instead of round for basedynamc
        self.body.update_true_pos_y(dt)
        self.delta = [self.hitbox.left - self.old_hitbox.left, self.hitbox.top  - self.old_hitbox.top]        

    def collide_x(self, entity):  # Handles horizontal collision
        if entity.hitbox.right >= self.hitbox.left and entity.old_hitbox.right <= self.old_hitbox.left:
            entity.platform_physics.resolve_side_collision(self, 'right')
        if entity.hitbox.left <= self.hitbox.right and entity.old_hitbox.left >= self.old_hitbox.right:
            entity.platform_physics.resolve_side_collision(self, 'left')
        entity.body.update_rect_x()

    def pre_entity_y_collision(self, entity):
        if self.delta[0] == 0 and self.delta[1] == 0:
            return False

        old_platform_hitbox = self.old_hitbox

        eps = 2
        was_on_top = abs(entity.old_hitbox.bottom - old_platform_hitbox.top) <= eps
        overlap_x = (
            entity.old_hitbox.right > old_platform_hitbox.left and
            entity.old_hitbox.left < old_platform_hitbox.right
        )

        if not (was_on_top and overlap_x):
            return False

        entity.true_pos[0] += self.delta[0]
        entity.true_pos[1] += self.delta[1]
        entity.rect.left = round(entity.true_pos[0])
        entity.rect.top = round(entity.true_pos[1])
        entity.body.update_hitbox()
        return True

    def collide_y(self, entity):#vertical collision
        if entity.hitbox.bottom >= self.hitbox.top and entity.old_hitbox.bottom <= self.old_hitbox.top:
            # Now resolve as grounded
            entity.platform_physics.resolve_vertical_collision(self, 'bottom')
            entity.platform_physics.limit_y()

        elif entity.hitbox.top <= self.hitbox.bottom and entity.old_hitbox.top >= self.old_hitbox.bottom:
            entity.platform_physics.resolve_vertical_collision(self, 'top')
        entity.body.update_rect_y()  # Update player’s vertical position
