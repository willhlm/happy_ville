import sys

class WeatherFXStates():
    def __init__(self, entity):
        self.entity = entity

    def update(self, dt):
        pass

    def enter_state(self, newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate.capitalize())(self.entity)#make a class based on the name of the newstate: need to import sys

    def draw(self, target):
        pass

class Idle(WeatherFXStates):
    def __init__(self,entity):
        super().__init__(entity)                

class Wind(WeatherFXStates):
    def __init__(self, entity):
        super().__init__(entity)
        self.time = 0

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.entity.game_objects.shaders['noise_perlin']['u_resolution'] = self.entity.game_objects.game.window_size
        self.entity.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.01
        self.entity.game_objects.shaders['noise_perlin']['scroll'] = [self.entity.parallax[0] * self.entity.game_objects.camera_manager.camera.scroll[0],-self.entity.game_objects.camera_manager.camera.scroll[1] * self.entity.parallax[1]]
        self.entity.game_objects.shaders['noise_perlin']['scale'] = [1,30]#long in x, short in y
        self.entity.game_objects.game.display.render(self.entity.image.texture, self.entity.noise_layer, shader = self.entity.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.entity.game_objects.shaders['wind']['noiseTexture'] = self.entity.noise_layer.texture
        self.entity.game_objects.shaders['wind']['time'] = self.time * 0.01
        self.entity.game_objects.shaders['wind']['velocity'] = self.entity.game_objects.weather.wind.velocity
        self.entity.game_objects.shaders['wind']['lifetime'] = self.entity.game_objects.weather.wind.lifetime
        
        self.entity.game_objects.game.display.render(self.entity.image.texture, target, shader = self.entity.game_objects.shaders['wind'])              