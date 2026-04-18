class PointArrow:
    def __init__(self, game_objects, pos=(0, 0), dir=None):
        self.game_objects = game_objects
        self.image = PointArrow.image
        self.world_pos = list(pos)
        self.time = 0
        self.dir = list(dir or [0, -1])

    def update(self, dt):
        self.time += dt

    def set_pos(self, pos):
        self.world_pos[0] = pos[0]
        self.world_pos[1] = pos[1]

    def pool(game_objects):
        size = (200,100)#to make the arrow more uniform when roated
        PointArrow.image = game_objects.game.display.make_layer(size)

    def draw(self, target):
        self.game_objects.shaders['arrow']['TIME'] = self.time*0.01
        self.game_objects.shaders['arrow']['moonDirection'] = self.dir
        pos = (
            int(self.world_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),
            int(self.world_pos[1] - self.game_objects.camera_manager.camera.scroll[1]),
        )
        self.game_objects.game.display.render(
            self.image.texture,
            target,
            position=pos,
            shader=self.game_objects.shaders['arrow'],
        )
