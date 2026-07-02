from gameplay.entities.base.static_entity import StaticEntity


class Rift(StaticEntity):
    def __init__(self, pos, game_objects, size, parallax, layer_name, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.parallax = parallax
        self.layer_name = layer_name
        self.time = 0

    def update(self, dt):
        super().update(dt)
        self.time += dt * 0.1

    def release_texture(self):
        self.image.release()

    def draw(self, target):
        screen_copy = self.game_objects.game.screen_manager.get_screen(layer=self.layer_name, include=False)
        self.game_objects.shaders['rift']['time'] = self.time
        self.game_objects.shaders['rift']['resolution'] = self.size
        self.game_objects.shaders['rift']['SCREEN_TEXTURE'] = screen_copy.texture
        pos = (
            int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),
            int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.interp_scroll[1]),
        )
        self.game_objects.shaders['rift']['section'] = [pos[0], pos[1], self.size[0], self.size[1]]
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['rift'])#shader render
