from gameplay.entities.base.static_entity import StaticEntity


class SpiritFlash(StaticEntity):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.size = tuple(kwargs.get("size", (420, 420)))
        self.image = game_objects.game.display.make_layer(self.size)
        self.empty = game_objects.game.display.make_layer(self.size)
        self.rect.size = self.size
        self.rect.center = pos
        self.true_pos = list(self.rect.topleft)

        self.start_scale = float(kwargs.get("start_scale", 0.35))
        self.scale = self.start_scale
        self.end_scale = float(kwargs.get("end_scale", 1.7))
        total_duration = max(float(kwargs.get("duration", 24)), 1.0)
        self.grow_duration = float(kwargs.get("grow_duration", total_duration * 0.55))
        self.hold_duration = float(kwargs.get("hold_duration", total_duration * 0.15))
        self.fade_duration = float(kwargs.get("fade_duration", max(total_duration - self.grow_duration - self.hold_duration, 1.0)))
        self.duration = self.grow_duration + self.hold_duration + self.fade_duration
        self.elapsed = 0.0
        self.start_alpha = float(kwargs.get("alpha", 255))
        self.current_alpha = self.start_alpha

        self.radius = float(kwargs.get("radius", min(self.size) * 0.42))
        self.radius_scale = float(kwargs.get("radius_scale", 1.0))
        self.alpha_scale = float(kwargs.get("alpha_scale", 1.0))
        self.gradient = float(kwargs.get("gradient", 0.78))
        self.colour = self._format_colour(kwargs.get("colour", [240, 250, 255, 255]))

    def update(self, dt):
        self.elapsed += dt
        grow_progress = min(self.elapsed / max(self.grow_duration, 1.0), 1.0)
        self.scale = self._lerp(self.start_scale, self.end_scale, grow_progress)

        fade_start = self.grow_duration + self.hold_duration
        if self.elapsed <= fade_start:
            self.current_alpha = self.start_alpha
        else:
            fade_progress = min((self.elapsed - fade_start) / max(self.fade_duration, 1.0), 1.0)
            self.current_alpha = self._lerp(self.start_alpha, 0.0, fade_progress)

        if self.elapsed >= self.duration or self.current_alpha <= 5:
            self.kill()

    def draw(self, target):
        self.image.clear(0, 0, 0, 0)
        self.empty.clear(0, 0, 0, 0)

        shader = self.game_objects.shaders["circle"]
        shader["size"] = self.size
        shader["radius"] = self.radius * self.radius_scale
        shader["color"] = (
            self.colour[0],
            self.colour[1],
            self.colour[2],
            self.current_alpha * self.alpha_scale,
        )
        shader["gradient"] = self.gradient
        self.game_objects.game.display.render(self.empty.texture, self.image, shader=shader)

        draw_width = self.size[0] * self.scale
        draw_height = self.size[1] * self.scale
        draw_pos = (
            int(self.rect.left - self.game_objects.camera_manager.camera.scroll[0] - (draw_width - self.size[0]) * 0.5),
            int(self.rect.top - self.game_objects.camera_manager.camera.scroll[1] - (draw_height - self.size[1]) * 0.5),
        )
        self.game_objects.game.display.use_premultiplied_alpha_mode()
        self.game_objects.game.display.render(
            self.image.texture,
            target,
            position=draw_pos,
            scale=(self.scale, self.scale),
        )
        self.game_objects.game.display.use_standard_alpha_mode()

    def release_texture(self):
        self.image.release()
        self.empty.release()

    @staticmethod
    def _lerp(start, end, progress):
        return start + (end - start) * progress

    @staticmethod
    def _format_colour(colour):
        channels = list(colour)
        if len(channels) == 3:
            channels.append(255)
        if all(channel <= 1 for channel in channels):
            return tuple(channel * 255 for channel in channels[:4])
        return tuple(channels[:4])
