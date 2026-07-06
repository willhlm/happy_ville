from gameplay.entities.base.static_entity import StaticEntity


class EnemySpawnEffect(StaticEntity):
    def __init__(
        self,
        pos,
        game_objects,
        preset="enemy_spawn_burst",
        count=10,
        sound="enemy_spawn",
        sound_volume=0.3,
        play_sound=True,
        **kwargs,
    ):
        super().__init__(pos, game_objects)
        if play_sound and sound:
            self.game_objects.sound.play_spawn_sound(sound, volume=sound_volume)
        self.game_objects.particles.emit(preset, pos, n=count, **kwargs)
        self.kill()

    def draw(self, target):
        pass
