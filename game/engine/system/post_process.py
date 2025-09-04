from engine.system import shaders

class PostProcess():#for screen-wide effects
    def __init__(self, game_objects, default_shader = 'vignette', **kwargs):
        self.game_objects = game_objects                        
        self.temp_layer = game_objects.game.display.make_layer(game_objects.game.display_size)    # Create temp buffer at display resolution
        self.shaders = {}
        if default_shader:
            self.set_shader(default_shader, **kwargs)

    def update_render(self, dt):
        self.update(dt)

    def apply(self, composite_screen):#called from gameplay state
        """Apply shaders to composite_screen, modifying it in place"""
        self.draw(composite_screen)

    def update(self, dt):
        for shader_obj in list(self.shaders.values()):
            shader_obj.update_render(dt)

    def draw(self, composite_screen):        
        shader_items = self.shaders.items()
        
        for i, (key, shader_obj) in enumerate(shader_items):   
            is_last_shader = (i == len(shader_items) - 1)
            self.temp_layer.clear(0, 0, 0, 0)

            if is_last_shader:# Last shader renders back to composite_screen                
                shader_obj.draw_to_composite(self.temp_layer, composite_screen)                
            else:# Intermediate shader renders to temp buffer                                                
                composite_screen = shader_obj.draw(self.temp_layer, composite_screen)

    def set_shader(self, shader_name, **kwargs):
        self.shaders = {}
        self.append_shader(shader_name, **kwargs)
        
    def append_shader(self, shader_name, **kwargs):        
        shader_class = getattr(shaders, shader_name.capitalize())
        self.shaders[shader_name] = shader_class(self, **kwargs)

    def remove_shader(self, shader):
        self.shaders.pop(shader, None)

class EntityProcess(PostProcess):#for entity overlay effects
    def __init__(self, entity):   
        self.entity = entity             
        self.shaders = {}

    def define_size(self, size):
        self.base_layer = self.entity.game_objects.game.display.make_layer(size)
        self.temp_layer = self.entity.game_objects.game.display.make_layer(size)        

    def draw(self, base_texture, target, position, flip):
        """Apply overlay shaders to base_texture, last shader draws to target."""  
        self.base_layer.clear(0, 0, 0, 0)
        self.temp_layer.clear(0, 0, 0, 0)        
        
        dst = self.temp_layer
        src = self.entity.shader_state.states.draw(base_texture, self.base_layer, position = (0, 0), flip = False)        

        shader_items = list(self.shaders.items())

        for i, (name, shader_obj) in enumerate(shader_items):
            is_last_shader = (i == len(shader_items) - 1)

            if is_last_shader:                
                shader_obj.draw_to_composite(src, target, position, flip)# Last shader draws to final target
            else:                
                src = shader_obj.draw(src, dst)# Intermediate shader: draw src -> dst

    def append_shader(self, shader_name, **kwargs):        
        shader_class = getattr(shaders, shader_name.capitalize())
        self.shaders[shader_name] = shader_class(self.entity.game_objects, **kwargs)