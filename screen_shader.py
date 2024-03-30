import shaders

class Screen_shader():#Shaders applied to whole screen, Can do multiple ones
    def __init__(self, game_objects, default_shader = 'idle', **kwarg):
        self.game_objects = game_objects
        self.set_shader(default_shader, **kwarg)

    def update(self):
        shaders_keys = list(self.shaders.keys())
        for index in range(len(shaders_keys) - 1, -1, -1):#reverse order
            shader_program = shaders_keys[index]
            self.shaders[shader_program].update()

    def draw(self):
        shaders_keys = list(self.shaders.keys())
        for index in range(len(shaders_keys) - 1, -1, -1):#reverse order
            shader_program = shaders_keys[index]
            self.shaders[shader_program].draw()         

    def append_shader(self, shader, **kwarg):
        self.shaders[shader] = getattr(shaders, shader.capitalize())(self.game_objects, **kwarg)

    def set_shader(self, shader, **kwarg):#overrite
        self.shaders = {}#clearn it
        self.append_shader(shader, **kwarg)

    def remove_shader(self,shader):
        self.shaders.pop(shader, None)

    @classmethod
    def pool(cls, game_objects):
        cls.layer = game_objects.game.display.make_layer(game_objects.game.screen.size)#this is shared in memory