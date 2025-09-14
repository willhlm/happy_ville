from gameplay.entities.base.static_entity import StaticEntity

class Rainbow(StaticEntity):#rainbow
    def __init__(self, pos, game_objects, size, parallax, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.parallax = parallax

    def release_texture(self):
        self.image.release()

    def draw(self, target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['rainbow'])#shader render    