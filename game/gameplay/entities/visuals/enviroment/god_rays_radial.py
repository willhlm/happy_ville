from gameplay.entities.base.static_entity import StaticEntity

class GodRaysRadial(StaticEntity):
    def __init__(self, pos, game_objects, parallax, size, **properties):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.image = game_objects.game.display.make_layer(size).texture
        self.shader = game_objects.shaders['rays_radial']
        self.shader['resolution'] = self.game_objects.game.window_size
        self.time = 0
        self.colour = properties.get('colour',(1.0, 0.9, 0.65, 0.6))#colour
        self.edge_falloff_distance = properties.get('edge_falloff_distance',0.3)

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        self.shader['edge_falloff_distance'] = self.edge_falloff_distance
        self.shader['time'] = self.time
        self.shader['size'] = self.image.size
        self.shader['color'] = self.colour

        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render