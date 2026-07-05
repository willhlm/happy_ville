from gameplay.entities.base.static_entity import StaticEntity

from . import states


class SpaceTimeCrack(StaticEntity):
    def __init__(self, pos, game_objects, size, parallax, layer_name, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.size = size
        self.rect.size = size
        self.rect.center = pos
        self.true_pos = list(self.rect.topleft)
        self.parallax = parallax
        self.layer_name = layer_name
        self.time = float(properties.get("time", 0))
        self.time_scale = float(properties.get("time_scale", 0.1))

        self.draw_scale = float(properties.get("draw_scale", 1.0))
        
        self.tint = tuple(properties.get("tint", (1.0, 1.0, 1.0, 1.0)))
        self.refraction_offset = tuple(properties.get("refraction_offset", (18.0, 18.0)))
        self.field_strength = float(properties.get("field_strength", 0.018))
        self.field_density = float(properties.get("field_density", 5.5))
        self.edge_fade = float(properties.get("edge_fade", 0.2))
        self.radial_fade_scale = float(properties.get("radial_fade_scale", 1))
        self.radial_fade_inner = float(properties.get("radial_fade_inner", 0.18))
        self.radial_field_inner = float(properties.get("radial_field_inner", 0.22))

        initial_state = properties.get("state", "idle")
        state_kwargs = properties.get("state_kwargs", {})
        self.enter_state(initial_state, **state_kwargs)

    def enter_state(self, state_name, **kwargs):
        self.currentstate = states.STATE_TYPES[state_name](self, **kwargs)

    def update(self, dt):
        super().update(dt)
        self.time += dt * self.time_scale
        self.currentstate.update(dt)

    def release_texture(self):
        self.image.release()

    def draw(self, target):
        screen_copy = self.game_objects.game.screen_manager.get_screen(layer=self.layer_name, include=False)
        shader = self.game_objects.shaders["space_time_crack"]
        shader["time"] = self.time
        shader["resolution"] = self.size
        shader["SCREEN_TEXTURE"] = screen_copy.texture
        shader["refraction_offset"] = self.refraction_offset
        shader["field_strength"] = self.field_strength
        shader["field_density"] = self.field_density
        shader["edge_fade"] = self.edge_fade
        shader["radial_fade_scale"] = self.radial_fade_scale
        shader["radial_fade_inner"] = self.radial_fade_inner
        shader["radial_field_inner"] = self.radial_field_inner
        width = int(self.size[0] * self.draw_scale)
        height = int(self.size[1] * self.draw_scale)
        pos = (
            int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0] - (width - self.size[0]) * 0.5),
            int(self.true_pos[1] - self.parallax[1] * self.game_objects.camera_manager.camera.interp_scroll[1] - (height - self.size[1]) * 0.5),
        )
        shader["section"] = [pos[0], pos[1], width, height]
        self.game_objects.game.display.render(
            self.image.texture,
            target,
            position=pos,
            scale=(self.draw_scale, self.draw_scale),
            shader=shader,
        )
