from gameplay.entities.enviroment.base.layered_objects import LayeredObjects

class BaseDynamic(LayeredObjects):
    def __init__(self,pos,game_objects,parallax, layer_name, live_blur = False):
        super().__init__(pos,game_objects,parallax, layer_name, live_blur)
        self.velocity = [0,0]
        self.friction = [0.5,0]
        self.true_pos = pos

    def group_distance(self):
        pass

    def update(self, dt):
        super().update(dt)
        self.update_pos(dt)
        self.boundary()

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + dt * self.velocity[0]*self.parallax[0], self.true_pos[1] + dt * self.velocity[1]*self.parallax[1]]
        self.rect.topleft = self.true_pos.copy()

    def boundary(self):
        pass