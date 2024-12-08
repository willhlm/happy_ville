import shaders

class Screen_shader():#Shaders applied to whole screen, Can do multiple ones
    def __init__(self, game_objects, default_shader = 'vignette', **kwarg):
        self.game_objects = game_objects        
        self.layer = game_objects.game.display.make_layer(game_objects.game.screen.size)
        if not default_shader: return
        self.set_shader(default_shader, **kwarg)

    def update(self):
        shaders_keys = list(self.shaders.keys())
        for key in shaders_keys:
            self.shaders[key].update()

    def draw(self, target):        
        self.layer.clear(0, 0, 0, 0)#need it so that it doesn't leave a "stain" in the screen
        base_texture = self.layer.texture#texture
        for key in self.shaders.keys():        
            base_texture = self.shaders[key].draw(base_texture)             

        self.shaders[key].draw_screen(base_texture)#some shaders require last render to be done to screen
        
    def append_shader(self, shader, **kwarg):
        self.shaders[shader] = getattr(shaders, shader.capitalize())(self, **kwarg)

    def set_shader(self, shader, **kwarg):#overrite
        self.shaders = {}#clearn it
        self.append_shader(shader, **kwarg)

    def remove_shader(self,shader):
        self.shaders.pop(shader, None)

class Entity_shader(Screen_shader):#shader applied to enteties: not used yet -> can be but require multiple display.render for enteties to make it general
    def __init__(self, entity, default_shader = 'idle', **kwarg):        
        self.entity = entity
        self.game_objects = entity.game_objects
        self.layer = game_objects.game.display.make_layer(entity.image.size)#layer saved in pool of entity
        self.set_shader(default_shader, **kwarg)

    def draw(self, blit_pos, flip):       
        self.layer.clear(0,0,0,0)#need it so that it doesn't leave a "stain" in the screen                
        base_texture = self.entity.image
        for key in self.shaders.keys():#reverse order
            base_texture = self.shaders[key].draw(base_texture, blit_pos, flip) 
        
        self.shaders[key].draw_screen(base_texture, blit_pos, flip)#some shaders require last render to be done to screen            