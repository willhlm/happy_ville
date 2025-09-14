from gameplay.entities.platforms.texture.base_texture import BaseTexture

class BaseDynamic(BaseTexture):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.velocity = [0,0]

    def update(self, dt):
        super().update(dt)
        self.old_hitbox = self.hitbox.copy()#save old position before moving
        self.update_vel(dt)
        self.update_true_pos_x(dt)
        self.update_true_pos_y(dt)

    def update_true_pos_x(self):
        self.true_pos[0] += dt*self.velocity[0]
        self.rect.left = int(self.true_pos[0])#should be int
        self.hitbox.left = self.rect.left

    def update_true_pos_y(self):
        self.true_pos[1] += dt*self.velocity[1]
        self.rect.top = int(self.true_pos[1])#should be int
        self.hitbox.top = self.rect.top

    def collide_x(self, entity):  # Handles horizontal collision
        if entity.hitbox.right >= self.hitbox.left and entity.old_hitbox.right <= self.old_hitbox.left:
            entity.right_collision(self)
        if entity.hitbox.left <= self.hitbox.right and entity.old_hitbox.left >= self.old_hitbox.right:
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self, entity):  # Handles vertical collision
        if entity.hitbox.bottom >= self.hitbox.top and entity.old_hitbox.bottom <= self.old_hitbox.top:
            entity.down_collision(self)
            entity.limit_y()
        if entity.hitbox.top <= self.hitbox.bottom and entity.old_hitbox.top >= self.old_hitbox.bottom:
            entity.top_collision(self)
        entity.update_rect_y()  # Update player’s vertical position
