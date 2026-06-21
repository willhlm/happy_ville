import pygame

from gameplay.entities.base.static_entity import StaticEntity


class ShockWave(StaticEntity):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.size = tuple(kwargs.get('size', (640, 640)))
        self.reference_size = float(kwargs.get('reference_size', 140.0))
        self.image, self.empty_layer = game_objects.layer_resource_pool.acquire_named_layers('shock_wave', self.size, 2)

        self.rect = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.rect.center = pos
        self.true_pos = list(self.rect.topleft)

        self.time = 0
        self.emit_stop_time = 0
        self.emitting = 1

        self.speed = float(kwargs.get('speed', 2.2))
        self.frequency = float(kwargs.get('frequency', 6.0))
        self.width = float(kwargs.get('width', 0.05))
        self.fade = float(kwargs.get('fade', 0.7))
        self.radial_fade_power = float(kwargs.get('radial_fade_power', 1.0))
        self.sine_scale = float(kwargs.get('sine_scale', 10.0))
        self.sine_speed = float(kwargs.get('sine_speed', 1.0))
        self.sine_strength = float(kwargs.get('sine_strength', 0.04))
        self.noise_map_scale = tuple(kwargs.get('noise_map_scale', (2.0, 2.0)))
        self.noise_scale = float(kwargs.get('noise_scale', 2.0))
        self.noise_strength = float(kwargs.get('noise_strength', 0.015))
        self.noise_speed = float(kwargs.get('noise_speed', 0.05))        

        colour = kwargs.get('colour', (1.0, 1.0, 1.0, 1.0))
        if max(colour[:3]) > 1.0:
            self.wave_colour = tuple(channel / 255 for channel in colour[:4])
        else:
            self.wave_colour = tuple(colour)

        self.start_alpha = float(kwargs.get('alpha', 255))
        self.alpha = self.game_objects.fade.create('alpha', self.start_alpha)
        self.alpha_decay = float(kwargs.get('alpha_decay', 0.98))
        self.alpha.set(self.start_alpha)

    def update(self, dt):
        self.time += dt * 0.01
        self.alpha.decay(self.alpha_decay)
        if self.alpha.is_below(10):
            self.kill()

    def draw(self, target):
        self.image.clear(0, 0, 0, 0)
        self.empty_layer.clear(0, 0, 0, 0)

        shader = self.game_objects.shaders['shock_wave']
        shader['TIME'] = self.time
        shader['wave_color'] = self.wave_colour
        shader['speed'] = self.speed
        shader['frequency'] = self.frequency
        shader['width'] = self.width
        shader['fade'] = self.fade
        shader['radial_fade_power'] = self.radial_fade_power
        shader['center'] = (0.5, 0.5)
        shader['resolution'] = self.size
        shader['reference_size'] = self.reference_size
        shader['sine_scale'] = self.sine_scale
        shader['sine_speed'] = self.sine_speed
        shader['sine_strength'] = self.sine_strength
        shader['noise_scale'] = self.noise_scale
        shader['noise_strength'] = self.noise_strength
        shader['noise_speed'] = self.noise_speed
        shader['emit'] = self.emitting
        shader['emit_stop_time'] = self.emit_stop_time        

        display = self.game_objects.game.display
        display.use_alpha_blending(False)
        display.render(self.empty_layer.texture, self.image, shader=shader)
        display.use_alpha_blending(True)

        blit_pos = [
            int(self.rect.left - self.game_objects.camera_manager.camera.scroll[0]),
            int(self.rect.top - self.game_objects.camera_manager.camera.scroll[1]),
        ]
        self.alpha.render(self.image.texture, target, position=blit_pos)

    def release_texture(self):
        pass

    def stop_emitting(self, decay = 0.98):
        self.emitting = float(0)
        self.emit_stop_time = self.time
        self.alpha_decay = decay
