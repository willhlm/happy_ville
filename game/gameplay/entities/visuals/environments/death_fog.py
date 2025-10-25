from gameplay.entities.base.static_entity import StaticEntity
    
class DeathFog(StaticEntity):#2D explosion
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.size = size
        self.time = 0

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['death_fog']['TIME'] = self.time*0.01
        self.game_objects.shaders['death_fog']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['death_fog']['velocity'] = [0, 0]
        self.game_objects.shaders['death_fog']['fog_color'] = [0, 0, 0, 1]

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['death_fog'])#shader render        