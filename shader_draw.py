import shaders

class Shader_draw():#Shaders applied to whole screen, Can do multiple ones
    def __init__(self, game_objects, default_shader = 'idle', **kwarg):
        self.game_objects = game_objects
        self.layers = [game_objects.game.screen]#should be first
        self.set_shader(default_shader, **kwarg)

    def update(self):
        shaders_keys = list(self.shaders.keys())
        for index in range(len(shaders_keys) - 1, -1, -1):#reverse order
            shader_program = shaders_keys[index]
            self.shaders[shader_program].update()

    def draw(self):
        shaders_keys = list(self.shaders.keys())
        #layer = Shader_draw.layer
        for index in range(len(shaders_keys) - 1, -1, -1):#reverse order
            shader_program = shaders_keys[index]
            self.shaders[shader_program].draw()
            #self.game_objects.game.display.render(self.layers[index + 1].texture, self.layers[index], shader = self.game_objects.shaders[shader_program])

    def append_shader(self, shader, **kwarg):
        self.shaders[shader] = getattr(shaders, shader.capitalize())(self.game_objects, **kwarg)
        self.append_layer()

    def set_shader(self, shader, **kwarg):#overrite
        self.shaders = {}
        self.append_shader(shader, **kwarg)

    def remove_shader(self,shader):
        self.shaders.pop(shader, None)
        self.layers.pop()

    def append_layer(self):
        self.layers.append(Shader_draw.layer)

    @classmethod
    def pool(cls, game_objects):
        cls.layer = game_objects.game.display.make_layer(game_objects.game.screen.size)#this is shared in memory

class Shader_draw_entity(Shader_draw):#not sure how to deal with teh positin in draw. Should be the supplied one when blitting on screen- Pyjtherwise 0
    def __init__(self, game_objects, texture, default_shader = 'idle', **kwarg):
        self.game_objects = game_objects
        self.layers = [texture]#the image: should be firts
        self.set_shader(default_shader, **kwarg)
        self.layers.append(self.game_objects.game.screen)#should be last

    def draw(self, position):
        self.game_objects.game.display.render(self.layers[0], self.layers[1], pos = position, shader = self.game_objects.shaders[list(self.shaders.keys())[0]])

        for index, key in enumerate(list(self.shaders.keys())[1:], start=1):#do all but first one
            self.shaders[key].draw()
            self.game_objects.game.display.render(self.layers[index].texture, self.layers[index + 1], pos = position, shader = self.game_objects.shaders[key])
