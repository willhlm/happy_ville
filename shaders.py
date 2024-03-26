class Shaders():
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def update(self):
        pass

    def draw(self):
        pass

class Vignette(Shaders):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.colour = kwarg.get('colour',[0,0,0,1])#colour

    def set_colour(self, colour):
        self.colour = colour

    def draw(self):
        self.game_objects.shaders['vignette']['colour'] = self.colour
        self.game_objects.game.display.render(self.game_objects.shader_draw.layer.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['vignette'])#shader render
        #return self.game_objects.game.screen#the result

class Chromatic_aberration(Shaders):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.duration = kwarg.get('duration',20)

    def update(self):
        self.duration -= self.game_objects.game.dt
        if self.duration < 0:
            self.game_objects.shader_draw.remove_shader('chromatic_aberration')

    def draw(self):
        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.game_objects.shader_draw.layer, shader = self.game_objects.shaders['chromatic_aberration'])#shader render
        self.game_objects.game.display.render(self.game_objects.shader_draw.layer.texture, self.game_objects.game.screen)#shader render

class Bloom(Shaders):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.radius = kwarg.get('bloomRadius',2)#colour
        self.bloomThreshold = kwarg.get('bloomThreshold',0.7)
        self.bloomIntensity = kwarg.get('bloomIntensity',1)#in pixels
        self.bloomTint = kwarg.get('bloomTint',[1,1,1])#between 0 and 1
        self.targetColor = kwarg.get('targetColor',[1,1,1])#between 0 and 1
        self.colorRange = kwarg.get('colorRange',1)#between 0 and 1

    def draw(self):
        self.game_objects.shaders['bloom']['bloomRadius'] = self.radius
        self.game_objects.shaders['bloom']['bloomIntensity'] = self.bloomIntensity
        self.game_objects.shaders['bloom']['bloomThreshold'] = self.bloomThreshold
        self.game_objects.shaders['bloom']['bloomTint'] = self.bloomTint
        self.game_objects.shaders['bloom']['targetColor'] = self.targetColor
        self.game_objects.shaders['bloom']['colorRange'] = self.colorRange

        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.game_objects.shader_draw.layer, shader = self.game_objects.shaders['bloom'])#shader render
        self.game_objects.game.display.render(self.game_objects.shader_draw.layer.texture, self.game_objects.game.screen)#shader render
        #return self.game_objects.shader_draw.layer#the result

class White_balance(Shaders):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)        

    def draw(self):
        self.game_objects.game.display.render(self.game_objects.game.screen.texture, self.game_objects.shader_draw.layer, shader = self.game_objects.shaders['white_balance'])#shader render
        self.game_objects.game.display.render(self.game_objects.shader_draw.layer.texture, self.game_objects.game.screen)#shader render
            