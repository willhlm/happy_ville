class EntityBody:
    def __init__(self, entity, anchor='midbottom'):
        self.entity = entity
        self.anchor = anchor

    def update_hitbox(self):
        setattr(self.entity.hitbox, self.anchor, getattr(self.entity.rect, self.anchor))

    def update_rect_y(self):
        setattr(self.entity.rect, self.anchor, getattr(self.entity.hitbox, self.anchor))
        self.entity.true_pos[1] = self.entity.rect.top

    def update_rect_x(self):
        setattr(self.entity.rect, self.anchor, getattr(self.entity.hitbox, self.anchor))
        self.entity.true_pos[0] = self.entity.rect.left

    def set_pos(self, pos):
        self.entity.rect.center = (pos[0], pos[1])
        self.entity.true_pos = list(self.entity.rect.topleft)
        setattr(self.entity.hitbox, self.anchor, getattr(self.entity.rect, self.anchor))

    def update_true_pos_x(self, dt):
        self.entity.true_pos[0] += dt * self.entity.velocity[0]
        self.entity.rect.left = round(self.entity.true_pos[0])
        self.update_hitbox()

    def update_true_pos_y(self, dt):
        self.entity.true_pos[1] += dt * self.entity.velocity[1]
        self.entity.rect.top = round(self.entity.true_pos[1])
        self.update_hitbox()
