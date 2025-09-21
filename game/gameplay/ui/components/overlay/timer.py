from gameplay.entities.base.static_entity import StaticEntity

class Timer(StaticEntity):#to display a timer on screen
    def __init__(self, entity, time):
        super().__init__([0,0], entity.game_objects)
        self.entity = entity
        self.time = time

    def update(self, dt):
        self.time -= dt
        if self.time < 0:
            self.entity.time_out()
            self.kill()

    def draw(self, target):
        string = str(round(self.time / 60, 2))#seconds¨
        size = (50,12)
        image = self.game_objects.font.render(size, string + ' seconds')
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(image, target, position = [self.game_objects.game.window_size[0] * 0.5 - size[0], self.game_objects.game.window_size[1] * 0.2], scale = [3,3], shader = self.game_objects.shaders['colour'])#shader render
        image.release()

    def release_texture(self):
        pass