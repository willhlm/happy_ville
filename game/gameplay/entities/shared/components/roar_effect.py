class RoarEffect:
    """Owns the shared audiovisual effects used while an entity roars."""

    def __init__(self, entity):
        self.entity = entity
        self.shader_name = None

    def start(
        self,
        *,
        amplitude=3,
        duration=100,
        scale=0.98,
        shader_name="Speed_lines",
        sound=None,
        sound_volume=0.8,
    ):
        self.stop()

        game_objects = self.entity.game_objects
        game_objects.camera_manager.camera_shake(
            amplitude=amplitude,
            duration=duration,
            scale=scale,
        )

        if shader_name:
            camera_scroll = game_objects.camera_manager.camera.scroll
            center = [
                self.entity.rect.centerx - camera_scroll[0],
                self.entity.rect.centery - camera_scroll[1],
            ]
            game_objects.post_process.append_shader(shader_name, center=center)
            self.shader_name = shader_name

        if sound is not None:
            game_objects.sound.play_sfx(sound, vol=sound_volume)

    def stop(self):
        if self.shader_name is None:
            return

        self.entity.game_objects.post_process.remove_shader(self.shader_name)
        self.shader_name = None
