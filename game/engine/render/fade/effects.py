from .controller import FadeController


class BaseFadeEffect:
    def __init__(self, fade_service, value=0.0, **kwargs):
        self.fade_service = fade_service
        self.game_objects = fade_service.game_objects
        self.controller = FadeController(
            value,
            min_value=kwargs.pop("min_value", 0.0),
            max_value=kwargs.pop("max_value", 255.0),
            on_complete=kwargs.pop("on_complete", None),
        )

    @property
    def value(self):
        return self.controller.value

    def set(self, value):
        return self.controller.set(value)

    def step(self, delta):
        return self.controller.step(delta)

    def step_linear(self, dt, speed):
        return self.controller.step_linear(dt, speed)

    def decay(self, rate):
        return self.controller.decay(rate)

    def approach(self, target, speed, dt, *, dt_scale=0.01):
        return self.controller.approach(target, speed, dt, dt_scale=dt_scale)

    def is_below(self, threshold):
        return self.controller.is_below(threshold)

    def complete(self):
        return self.controller.complete()

    def render(self, source, target, **render_kwargs):
        raise NotImplementedError

    def release(self):
        pass


class AlphaFadeEffect(BaseFadeEffect):
    def render(
        self,
        source,
        target,
        *,
        amount=None,
        position=(0, 0),
        flip=False,
        angle=0,
        **render_kwargs,
    ):
        shader = self.game_objects.shaders["alpha"]
        shader["alpha"] = self.value if amount is None else amount
        self.game_objects.game.display.render(
            source,
            target,
            position=position,
            flip=flip,
            angle=angle,
            shader=shader,
            **render_kwargs,
        )


class DissolveFadeEffect(BaseFadeEffect):
    def __init__(self, fade_service, value=0.0, **kwargs):
        self.dissolve_texture = kwargs.pop("dissolve_texture", None)
        self.burn_color = kwargs.pop("burn_color", (0.6, 0.5, 0.9, 1.0))
        self.burn_size = kwargs.pop("burn_size", 0.1)
        self.noise_scale = kwargs.pop("noise_scale", (10, 10))
        self.noise_time = kwargs.pop("noise_time", 0.0)
        self.noise_scroll = kwargs.pop("noise_scroll", (0, 0))
        self._generated_noise_layers = {}
        self._generated_empty_layers = {}
        super().__init__(fade_service, value, **kwargs)

    def render(
        self,
        source,
        target,
        *,
        amount=None,
        position=(0, 0),
        flip=False,
        angle=0,
        dissolve_texture=None,
        burn_color=None,
        burn_size=None,
        noise_scale=None,
        noise_time=None,
        noise_scroll=None,
        **render_kwargs,
    ):
        shader = self.game_objects.shaders["dissolve"]
        texture_size = self._texture_size(source)
        dissolve_texture = dissolve_texture or self.dissolve_texture
        burn_color = self.burn_color if burn_color is None else burn_color
        burn_size = self.burn_size if burn_size is None else burn_size
        noise_scale = self.noise_scale if noise_scale is None else noise_scale
        noise_time = self.noise_time if noise_time is None else noise_time
        noise_scroll = self.noise_scroll if noise_scroll is None else noise_scroll

        if dissolve_texture is None:
            dissolve_texture = self._build_dissolve_noise(
                texture_size,
                noise_time=noise_time,
                noise_scale=noise_scale,
                noise_scroll=noise_scroll,
            )

        coverage = self._normalize_coverage(self.value if amount is None else amount)
        shader["dissolve_texture"] = dissolve_texture
        shader["dissolve_value"] = 1.0 - coverage
        shader["burn_color"] = burn_color
        shader["burn_size"] = burn_size
        self.game_objects.game.display.render(
            source,
            target,
            position=position,
            flip=flip,
            angle=angle,
            shader=shader,
            **render_kwargs,
        )

    def release(self):
        for layer in self._generated_noise_layers.values():
            layer.release()
        for layer in self._generated_empty_layers.values():
            layer.release()
        self._generated_noise_layers.clear()
        self._generated_empty_layers.clear()

    def _build_dissolve_noise(self, texture_size, *, noise_time, noise_scale, noise_scroll):
        noise_layer, empty_layer = self._get_noise_layers(texture_size)
        empty_layer.clear(0, 0, 0, 0)

        noise_shader = self.game_objects.shaders["noise_perlin"]
        noise_shader["u_resolution"] = texture_size
        noise_shader["u_time"] = noise_time
        noise_shader["scroll"] = noise_scroll
        noise_shader["scale"] = noise_scale
        self.game_objects.game.display.render(
            empty_layer.texture,
            noise_layer,
            shader=noise_shader,
        )
        return noise_layer.texture

    def _get_noise_layers(self, texture_size):
        size = tuple(texture_size)
        noise_layer = self._generated_noise_layers.get(size)
        empty_layer = self._generated_empty_layers.get(size)
        if noise_layer is None or empty_layer is None:
            display = self.game_objects.game.display
            noise_layer = display.make_layer(size)
            empty_layer = display.make_layer(size)
            self._generated_noise_layers[size] = noise_layer
            self._generated_empty_layers[size] = empty_layer
        return noise_layer, empty_layer

    def _normalize_coverage(self, amount):
        value = float(amount)
        if value <= 1.0:
            return max(0.0, min(1.0, value))
        return max(0.0, min(1.0, value / 255.0))

    def _texture_size(self, source):
        size = getattr(source, "size", None)
        if size is not None:
            return tuple(size)
        return (int(source.width), int(source.height))


class MaskFadeEffect(BaseFadeEffect):
    def __init__(self, fade_service, value=0.0, **kwargs):
        self.mask_texture = kwargs.pop("mask_texture", None)
        self.mask_kind = kwargs.pop("mask_kind", "horizontal")
        self.mask_params = dict(kwargs.pop("mask_params", {}))
        self.invert = kwargs.pop("invert", False)
        self.feather = kwargs.pop("feather", 0.02)
        super().__init__(fade_service, value, **kwargs)

    def render(
        self,
        source,
        target,
        *,
        amount=None,
        position=(0, 0),
        flip=False,
        angle=0,
        mask_texture=None,
        mask_kind=None,
        invert=None,
        feather=None,
        mask_params=None,
        **render_kwargs,
    ):
        shader = self.game_objects.shaders["fading"]
        coverage = self._normalize_coverage(self.value if amount is None else amount)
        feather = self.feather if feather is None else feather
        invert = self.invert if invert is None else invert
        resolved_mask_texture = mask_texture or self.mask_texture

        if resolved_mask_texture is None:
            texture_size = self._texture_size(source)
            resolved_mask_texture = self.fade_service.masks.get(
                mask_kind or self.mask_kind,
                texture_size,
                **(self.mask_params | (mask_params or {})),
            )

        shader["mask_texture"] = resolved_mask_texture
        shader["threshold"] = self._threshold_from_coverage(coverage, feather)
        shader["feather"] = feather
        shader["invert"] = invert
        self.game_objects.game.display.render(
            source,
            target,
            position=position,
            flip=flip,
            angle=angle,
            shader=shader,
            **render_kwargs,
        )

    def _normalize_coverage(self, amount):
        value = float(amount)
        if value <= 1.0:
            return max(0.0, min(1.0, value))
        return max(0.0, min(1.0, value / 255.0))

    def _threshold_from_coverage(self, coverage, feather):
        return (1.0 + feather) - coverage * (1.0 + 2.0 * feather)

    def _texture_size(self, source):
        size = getattr(source, "size", None)
        if size is not None:
            return tuple(size)
        return (int(source.width), int(source.height))
