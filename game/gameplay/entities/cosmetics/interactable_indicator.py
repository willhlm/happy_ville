from gameplay.entities.base.static_entity import StaticEntity

class InteractableIndicator(StaticEntity):#the hoovering above things to indicat it is interactable, or only for NPC?
    def __init__(self, pos, game_objects, size = (32,32)):
        super().__init__(pos, game_objects)
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        InteractableIndicator.image = game_objects.font.fill_text_bg(size, 'text_bubble')

    def release_texture(self):
        pass

    def update(self, dt):
        self.time += dt * 0.1
        self.update_vel()
        self.update_pos(dt)

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0] * dt, self.true_pos[1] + self.velocity[1] * dt]
        self.rect.topleft = self.true_pos

    def update_vel(self):
        self.velocity[1] = 0.25*math.sin(self.time)
