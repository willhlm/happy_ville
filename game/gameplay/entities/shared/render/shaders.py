class Shaders():
    def __init__(self, post_process):
        self.post_process = post_process#TODO change this to game_objects

    def update_render(self, dt):
        pass

    def set_uniforms(self, **kwargs):#is also called from screen layers
        pass

    def draw(self, temp_layer, input_layer):#called for screen pp (small resolution) and composiite pp (scaled resolution)
        """Draw to intermediate texture for pipeline"""
        pass

    def draw_to_composite(self, temp_layer, final_layer):#only called for composite pp -> sacled resoltuoin
        """Draw final result back to composite_screen"""
        pass
        
class Aura(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects    
        self.time = 0
        self.colour = kwarg.get('colour', [0.3, 0.7, 1.0])
        self.size = kwarg.get('size', 0.2)
        self.fall_off = kwarg.get('fall_off', 2)
        self.noise_intensity = kwarg.get('noise_intensity', 5)

    def update_render(self, dt):
        self.time += dt * 0.1
 
    def set_uniforms(self):
        self.game_objects.shaders['aura']['TIME'] = self.time
        self.game_objects.shaders['aura']['AuraProgres'] = 1 
        self.game_objects.shaders['aura']['aura_color'] = self.colour 
        self.game_objects.shaders['aura']['AuraSize'] = self.size 
        self.game_objects.shaders['aura']['AuraFalloff'] = self.fall_off 
        self.game_objects.shaders['aura']['NoiseIntensity'] = self.noise_intensity 

    def draw(self, source_texture, composite_screen):
        """For intermediate rendering in pipeline"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['aura'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip):
        """Final render back to composite_screen"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip = flip, shader=self.game_objects.shaders['aura'])

class Outline(Shaders):
    def __init__(self,game_objects, **kwarg):
        self.game_objects = game_objects    
        self.colour = kwarg.get('colour', [1, 1, 1, 1])
        self.thickness = kwarg.get('thickness', 5)
        self.falloff = kwarg.get('falloff', 0)
        self.time = 0

    def update(self, dt):
        self.time += dt

    def set_uniforms(self):
        self.game_objects.shaders['outline']['outlineColor'] = self.colour
        self.game_objects.shaders['outline']['outlineThickness'] = self.thickness
        self.game_objects.shaders['outline']['outlineAlphaFalloff'] = self.falloff

    def draw(self, source_texture, composite_screen):
        """For intermediate rendering in pipeline"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader = self.game_objects.shaders['outline'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip):
        """Final render back to composite_screen"""
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip = flip, shader = self.game_objects.shaders['outline']) 
