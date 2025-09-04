from gameplay.entities.states import shader_states
from engine.system.post_process import EntityProcess

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


