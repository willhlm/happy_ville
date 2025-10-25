from . import shader_states
from engine.render.post_process import PostProcess
from engine.system import shaders

class EntityShaderManager():
    def __init__(self, entity, default = 'idle', **kwargs):
        self.entity = entity
        self.enter_state(default, **kwargs)
        self.effects = EntityProcess(entity)               # Overlay effects pipeline

    def define_size(self, size):
        self.effects.define_size(size)

    # --- State handling ---
    def enter_state(self, new_state, **kwargs):
        self.states = getattr(shader_states, new_state.capitalize())(self.entity, **kwargs)#make a class based on the name of the newstate: need to import sys

    def handle_input(self, input, **kwargs):
        self.states.handle_input(input, **kwargs)

    # --- Effect handling ---
    def add_shader(self, name, **kwargs):
        self.effects.append_shader(name, **kwargs)

    def remove_shader(self, name):
        self.effects.remove_shader(name)

    def update_render(self, dt):
        self.states.update_render(dt)
        self.effects.update_render(dt)

    # --- Drawing ---
    def draw(self, base_texture, target, position, flip = False):        
        if not self.effects.shaders:
            self.states.draw(base_texture, target, position, flip)# If no overlay effects, render base shader directly
            return
                
        self.effects.draw(base_texture, target, position, flip) # Pass through overlay pipeline

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
