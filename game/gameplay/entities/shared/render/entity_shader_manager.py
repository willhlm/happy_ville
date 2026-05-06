from .entity_effect_pipeline import EntityEffectPipeline
from .entity_shader_state_controller import EntityShaderStateController

class EntityShaderManager():
    def __init__(self, entity, default='idle', **kwargs):
        self.entity = entity
        self.state_controller = EntityShaderStateController(entity, default, **kwargs)
        self.effects = EntityEffectPipeline(entity, self.state_controller)

    def enter_state(self, new_state, **kwargs):
        self.state_controller.enter_state(new_state, **kwargs)

    def handle_input(self, input_name, **kwargs):
        self.state_controller.handle_input(input_name, **kwargs)

    def add_shader(self, name, **kwargs):
        self.effects.append_shader(name, **kwargs)

    def remove_shader(self, name):
        self.effects.remove_shader(name)

    def update_render(self, dt):
        self.state_controller.update_render(dt)
        self.effects.update_render(dt)

    def draw(self, base_texture, target, position, flip=False, angle=0):
        if not self.effects.has_shaders():
            self.state_controller.draw(base_texture, target, position, flip, angle)
            self.draw_normal(position, flip, angle)
            return

        self.effects.draw(base_texture, target, position, flip, angle)
        self.draw_normal(position, flip, angle)

    def clear_textures(self):
        self.effects.clear_textures()

    def release(self):
        self.clear_textures()

    def draw_normal(self, position, flip=False, angle=0):
        normal_texture = self._current_normal_texture()
        if normal_texture is None:
            return

        self.entity.game_objects.shaders['normal_map']['direction'] = -self.entity.dir[0]
        self.entity.game_objects.game.display.render(
            normal_texture,
            self.entity.game_objects.lights.normal_map,
            position=position,
            flip=flip,
            angle=angle,
            shader=self.entity.game_objects.shaders['normal_map'],
        )

    def _current_normal_texture(self):
        sprites = getattr(self.entity, 'sprites', None)
        normal_maps = getattr(sprites, 'normal_maps', None)
        if not normal_maps:
            return None

        animation_name = self.entity.animation.animation_name
        image_frame = self.entity.animation.image_frame
        textures = normal_maps.get(animation_name)

        return textures[image_frame]
