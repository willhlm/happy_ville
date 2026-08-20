from gameplay.entities.base.static_entity import StaticEntity

class GodRays(StaticEntity):
    """Screen-space directional god rays configured by a Tiled object.

    ``angle`` is stored in radians; the static spawner converts the Tiled
    degree value before constructing this object. The shader derives an
    imaginary source on the render boundary from the ray direction.
    ``pixel_size`` controls the size of the snapped game-pixel blocks.
    """
    def __init__(self, pos, game_objects, parallax, size, **properties):
        super().__init__(pos, game_objects)
        self.parallax = parallax
        self.image = game_objects.game.display.make_layer(size).texture
        self.shader = game_objects.shaders['rays']
        self.shader['resolution'] = self.game_objects.game.window_size
        self.time = 0
        self.colour = properties.get('colour',(1.0, 0.9, 0.65, 0.6))#colour
        self.angle = properties.get('angle',-0.2)  # Radians: Tiled 0° is vertical; 90° is horizontal.
        self.falloff = properties.get('falloff',(0,0.3))#between 0 and 1
        self.pixel_size = max(float(properties.get('pixel_size', 1)), 1.0)  # Logical game pixels per ray block.

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.1

    def draw(self, target):
        self.shader['angle'] = self.angle
        self.shader['falloff'] = self.falloff
        self.shader['pixelSizeScale'] = self.pixel_size
        self.shader['time'] = self.time
        self.shader['color'] = self.colour

        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)#shader render
