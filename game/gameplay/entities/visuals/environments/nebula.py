from gameplay.entities.base.static_entity import StaticEntity

class Nebula(StaticEntity):#can be used as soul?
    def __init__(self, pos, game_objects, size, parallax):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.parallax = parallax
        self.size = size
        self.time = 0

    def update(self, dt):
        self.time += dt * 0.1

    def draw(self, target):
        self.game_objects.shaders['nebula']['time'] = self.time
        self.game_objects.shaders['nebula']['resolution'] = self.size

        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['nebula'])#shader render        