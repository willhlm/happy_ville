from gameplay.entities.base.static_entity import StaticEntity

class PointArrow(StaticEntity):#for thuder charge state
    def __init__(self, pos, game_objects, dir = [0, -1]):
        super().__init__(pos, game_objects)
        self.image = PointArrow.image
        self.time = 0
        self.dir = dir#default direction

    def release_texture(self):
        pass

    def update(self, dt):
        self.time += dt

    def pool(game_objects):
        size = (200,100)#to make the arrow more uniform when roated
        PointArrow.image = game_objects.game.display.make_layer(size)

    def draw(self, target):
        self.game_objects.shaders['arrow']['TIME'] = self.time*0.01
        self.game_objects.shaders['arrow']['moonDirection'] = self.dir

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['arrow'])#shader render   