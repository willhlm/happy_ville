from .base import Shaders


class Aura(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.time = 0
        colour = kwarg.get('colour', [77, 179, 255])
        self.colour = [channel / 255 for channel in colour[:3]]
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
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['aura'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip=flip, angle=angle, shader=self.game_objects.shaders['aura'])


class Outline(Shaders):
    def __init__(self, game_objects, **kwarg):
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
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['outline'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip=flip, angle=angle, shader=self.game_objects.shaders['outline'])


class Sway(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.time = 0
        self.offset = kwarg.get('offset', 0.0)
        self.speed = kwarg.get('speed', 0.01)
        self.min_strength = kwarg.get('min_strength', 0.01)
        self.max_strength = kwarg.get('max_strength', 0.05)
        self.strength_scale = kwarg.get('strength_scale', 13.0)
        self.interval = kwarg.get('interval', 3.5)
        self.detail = kwarg.get('detail', 1.0)
        self.height_offset = kwarg.get('height_offset', 0.1)
        self.upsidedown = kwarg.get('upsidedown', 0.0)

    def update_render(self, dt):
        self.time += dt

    def set_uniforms(self):
        shader = self.game_objects.shaders['sway_wind']
        shader['TIME'] = self.time
        shader['offset'] = self.offset
        shader['speed'] = self.speed
        shader['minStrength'] = self.min_strength
        shader['maxStrength'] = self.max_strength
        shader['strengthScale'] = self.strength_scale
        shader['interval'] = self.interval
        shader['detail'] = self.detail
        shader['heightOffset'] = self.height_offset
        shader['upsidedown'] = self.upsidedown

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['sway_wind'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position, flip=flip, angle=angle, shader=self.game_objects.shaders['sway_wind'])


class Tint(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.colour = kwarg.get('colour', [0, 0, 0, 0])

    def set_uniforms(self):
        self.game_objects.shaders['tint']['colour'] = self.colour

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['tint'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['tint'])


class Colour(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.colour = kwarg.get('colour', [1, 1, 1, 1])

    def set_uniforms(self):
        self.game_objects.shaders['colour']['colour'] = self.colour

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['colour'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['colour'])


class Mix_colour(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.colour = kwarg.get('colour', [1, 1, 1, 1])
        self.new_colour = kwarg.get('new_colour', [1, 1, 1, 1])
        self.position = kwarg.get('position', 0.0)

    def set_uniforms(self):
        shader = self.game_objects.shaders['mix_colour']
        shader['colour'] = self.colour
        shader['new_colour'] = self.new_colour
        shader['position'] = self.position

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['mix_colour'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['mix_colour'])


class Blur(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.blur_radius = float(kwarg.get('blur_radius', kwarg.get('radius', 0.1)))

    def update_render(self, dt):
        self.blur_radius += (1.1 - self.blur_radius) * 0.06
        self.blur_radius = min(1.1, self.blur_radius)

    def set_uniforms(self):
        self.game_objects.shaders['blur']['blurRadius'] = self.blur_radius

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.use_premultiplied_alpha_mode()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['blur'])
        self.game_objects.game.display.use_standard_alpha_mode()
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.use_premultiplied_alpha_mode()
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['blur'])
        self.game_objects.game.display.use_standard_alpha_mode()


class Mb(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.dir = kwarg.get('dir', [0.04, 0])
        self.quality = kwarg.get('quality', 6)

    def set_uniforms(self):
        self.game_objects.shaders['motion_blur']['dir'] = self.dir
        self.game_objects.shaders['motion_blur']['quality'] = self.quality

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['motion_blur'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['motion_blur'])


class Palette_swap(Shaders):
    MAX_PALETTE_SWAP_COLOURS = 32

    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.original_colour = kwarg.get('original_colour', [])
        self.replace_colour = kwarg.get('replace_colour', [])

    def set_uniforms(self):
        shader = self.game_objects.shaders['palette_swap']
        colour_count = min(
            len(self.original_colour),
            len(self.replace_colour),
            self.MAX_PALETTE_SWAP_COLOURS,
        )
        shader['number_colour'] = colour_count
        shader['original_colors'] = self._format_palette_uniform(self.original_colour, colour_count)
        shader['replace_colors'] = self._format_palette_uniform(self.replace_colour, colour_count)

    def _format_palette_uniform(self, colours, colour_count):
        padded = list(colours[:colour_count])
        padded.extend([(0, 0, 0, 0)] * (self.MAX_PALETTE_SWAP_COLOURS - colour_count))
        return tuple(tuple(colour) for colour in padded)

    def draw(self, source_texture, composite_screen):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['palette_swap'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['palette_swap'])


class Noise_border(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.time = 0

    def update_render(self, dt):
        self.time += dt * 0.01

    def set_uniforms(self, size):
        noise_layer, empty_layer = self.game_objects.layer_resource_pool.acquire_named_layers("noise_border", size, 2)
        empty_layer.clear(0, 0, 0, 0)
        noise = self.game_objects.shaders['noise_perlin']
        noise['u_resolution'] = size
        noise['u_time'] = self.time
        noise['scroll'] = [0, 0]
        noise['scale'] = [100, 100]
        self.game_objects.game.display.render(empty_layer.texture, noise_layer, shader=noise)

        shader = self.game_objects.shaders['noise_border']
        shader['TIME'] = self.time
        shader['textureNoise'] = noise_layer.texture

    def draw(self, source_texture, composite_screen):
        self.set_uniforms(source_texture.size)
        self.game_objects.game.display.render(source_texture.texture, composite_screen, shader=self.game_objects.shaders['noise_border'])
        return composite_screen

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms(source_texture.size)
        self.game_objects.game.display.render(source_texture.texture, target, position=position, flip=flip, angle=angle, shader=self.game_objects.shaders['noise_border'])

    @classmethod
    def flush_cache(cls):
        pass

    def release(self):
        pass

class Glow(Shaders):
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.glowIntensity = kwarg.get('intensity', 1)
        self.glowColor = kwarg.get('colour', (1, 1, 1))
        self.radialCenter = kwarg.get('radial_center', (0.5, 0.5))
        self.radialInner = kwarg.get('radial_inner', 0.0)
        self.radialOuter = kwarg.get('radial_outer', 0.2)

    def set_uniforms(self):
        shader = self.game_objects.shaders['glow']
        shader['glowIntensity'] = self.glowIntensity
        shader['glowColor'] = self.glowColor
        shader['radialCenter'] = self.radialCenter
        shader['radialInner'] = self.radialInner
        shader['radialOuter'] = self.radialOuter

    def _apply(self, source_layer, target_layer):
        self.set_uniforms()
        self.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            shader=self.game_objects.shaders['glow'],
        )
        return target_layer

    def draw(self, source_texture, composite_screen):
        return self._apply(source_texture, composite_screen)

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        self.set_uniforms()
        self.game_objects.game.display.render(
            source_texture.texture,
            target,
            position=position,
            flip=flip,
            angle=angle,
            shader=self.game_objects.shaders['glow'],
        )

class Transparent_outline(Shaders):#for bossess
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.layer_name = kwarg.get('layer_name', 'player')
        self.time = 0
        self.reveal = float(kwarg.get('reveal', 0.0))
        self.reveal_speed = float(kwarg.get('reveal_speed', 0.004))
        self.shine_colour = self._format_colour(
            kwarg.get('shine_colour', kwarg.get('outline_colour', kwarg.get('colour', [190, 225, 255, 235]))),
            default_alpha=1.0,
        )
        self.distortion_strength = float(kwarg.get('distortion_strength', 18.0))
        self.distortion_frequency = float(kwarg.get('distortion_frequency', 4.5))
        self.silhouette_alpha = float(kwarg.get('silhouette_alpha', 0.82))
        self.reveal_softness = float(kwarg.get('reveal_softness', 0.16))

    def update_render(self, dt):
        self.time += dt * 0.05
        if self.reveal_speed <= 0:
            return
        self.reveal = min(1.0, self.reveal + dt * self.reveal_speed)

    def set_uniforms(self):
        shader = self.game_objects.shaders['transparent_outline']
        shader['time'] = self.time
        shader['shine_color'] = self.shine_colour
        shader['reveal'] = self.reveal
        shader['reveal_softness'] = self.reveal_softness
        shader['distortion_strength'] = self.distortion_strength
        shader['distortion_frequency'] = self.distortion_frequency
        shader['silhouette_alpha'] = self.silhouette_alpha

    def _apply(self, source_layer, target_layer, position=(0, 0), flip=False, angle=0, screen_texture=None, section=None):
        self.set_uniforms()
        shader = self.game_objects.shaders['transparent_outline']
        shader['resolution'] = source_layer.size
        shader['SCREEN_TEXTURE'] = (screen_texture or source_layer.texture)
        shader['section'] = section or [0, 0, source_layer.size[0], source_layer.size[1]]
        self.game_objects.game.display.render(
            source_layer.texture,
            target_layer,
            position=position,
            flip=flip,
            angle=angle,
            shader=shader,
        )
        return target_layer

    def draw(self, source_texture, composite_screen):
        return self._apply(source_texture, composite_screen)

    def draw_to_composite(self, source_texture, target, position, flip, angle):
        screen_copy = self.game_objects.game.screen_manager.get_screen(layer=self.layer_name, include=False)
        section = [position[0], position[1], source_texture.size[0], source_texture.size[1]]
        self._apply(
            source_texture,
            target,
            position=position,
            flip=flip,
            angle=angle,
            screen_texture=screen_copy.texture,
            section=section,
        )

    @staticmethod
    def _format_colour(colour, default_alpha=1.0):
        channels = list(colour)
        if len(channels) == 3:
            channels.append(default_alpha)
        if any(channel > 1 for channel in channels):
            scale = 255
            channels = [channel / scale for channel in channels]
        return channels
