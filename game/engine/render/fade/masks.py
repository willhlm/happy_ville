import math

import pygame


class FadeMaskCache:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._textures = {}
        self._resources = {}

    def get(self, kind, size, **params):
        key = (kind, tuple(size), self._freeze(params))
        texture = self._textures.get(key)
        if texture is not None:
            return texture

        texture, resource = self._build(kind, tuple(size), **params)
        self._textures[key] = texture
        self._resources[key] = resource
        return texture

    def release(self):
        for resource in self._resources.values():
            if isinstance(resource, tuple):
                for item in resource:
                    item.release()
            else:
                resource.release()
        self._textures.clear()
        self._resources.clear()

    def _build(self, kind, size, **params):
        if kind == "horizontal":
            return self._texture_from_surface(self._build_horizontal(size, invert=params.get("invert", False)))
        if kind == "vertical":
            return self._texture_from_surface(self._build_vertical(size, invert=params.get("invert", False)))
        if kind == "radial":
            return self._texture_from_surface(self._build_radial(size, invert=params.get("invert", False)))
        if kind == "stripes":
            return self._texture_from_surface(
                self._build_stripes(
                    size,
                    count=params.get("count", 8),
                    axis=params.get("axis", "x"),
                    invert=params.get("invert", False),
                )
            )
        if kind == "noise":
            return self._build_noise(
                size,
                noise_time=params.get("noise_time", 0.0),
                scale=params.get("scale", (10, 10)),
                scroll=params.get("scroll", (0, 0)),
            )
        if kind == "swirl":
            return self._build_swirl(
                size,
                center=params.get("center", (0.5, 0.5)),
                turns=params.get("turns", 3.0),
                radial_bias=params.get("radial_bias", 1.0),
                angle_offset=params.get("angle_offset", 0.0),
            )
        raise ValueError(f"Unknown fade mask kind: {kind}")

    def _texture_from_surface(self, surface):
        texture = self.game_objects.game.display.surface_to_texture(surface)
        return texture, texture

    def _build_horizontal(self, size, *, invert=False):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        denom = max(width - 1, 1)
        for x in range(width):
            value = int(255 * (x / denom))
            if invert:
                value = 255 - value
            pygame.draw.line(surface, (value, value, value, 255), (x, 0), (x, height))
        return surface

    def _build_vertical(self, size, *, invert=False):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        denom = max(height - 1, 1)
        for y in range(height):
            value = int(255 * (y / denom))
            if invert:
                value = 255 - value
            pygame.draw.line(surface, (value, value, value, 255), (0, y), (width, y))
        return surface

    def _build_radial(self, size, *, invert=False):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        center_x = width * 0.5
        center_y = height * 0.5
        max_distance = max(math.hypot(center_x, center_y), 1.0)

        for y in range(height):
            for x in range(width):
                distance = math.hypot(x - center_x, y - center_y)
                value = int(255 * min(distance / max_distance, 1.0))
                if invert:
                    value = 255 - value
                surface.set_at((x, y), (value, value, value, 255))
        return surface

    def _build_stripes(self, size, *, count, axis, invert=False):
        width, height = size
        surface = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
        axis = axis.lower()
        span = width if axis == "x" else height
        stripe_size = max(span / max(count, 1), 1)

        for index in range(span):
            stripe_index = int(index / stripe_size)
            value = 255 if stripe_index % 2 == 0 else 0
            if invert:
                value = 255 - value
            color = (value, value, value, 255)
            if axis == "x":
                pygame.draw.line(surface, color, (index, 0), (index, height))
            else:
                pygame.draw.line(surface, color, (0, index), (width, index))
        return surface

    def _build_noise(self, size, *, noise_time, scale, scroll):
        display = self.game_objects.game.display
        target_layer = display.make_layer(size)
        empty_layer = display.make_layer(size)
        empty_layer.clear(0, 0, 0, 0)

        noise_shader = self.game_objects.shaders["noise_perlin"]
        noise_shader["u_resolution"] = size
        noise_shader["u_time"] = noise_time
        noise_shader["scale"] = scale
        noise_shader["scroll"] = scroll
        display.render(
            empty_layer.texture,
            target_layer,
            shader=noise_shader,
        )
        return target_layer.texture, (target_layer, empty_layer)

    def _build_swirl(self, size, *, center, turns, radial_bias, angle_offset):
        display = self.game_objects.game.display
        target_layer = display.make_layer(size)
        empty_layer = display.make_layer(size)
        empty_layer.clear(0, 0, 0, 0)

        swirl_shader = self.game_objects.shaders["swirl_mask"]
        swirl_shader["center"] = center
        swirl_shader["turns"] = turns
        swirl_shader["radial_bias"] = radial_bias
        swirl_shader["angle_offset"] = angle_offset
        display.render(
            empty_layer.texture,
            target_layer,
            shader=swirl_shader,
        )
        return target_layer.texture, (target_layer, empty_layer)

    def _freeze(self, value):
        if isinstance(value, dict):
            return tuple(sorted((key, self._freeze(val)) for key, val in value.items()))
        if isinstance(value, (list, tuple)):
            return tuple(self._freeze(item) for item in value)
        if isinstance(value, set):
            return tuple(sorted(self._freeze(item) for item in value))
        return value
