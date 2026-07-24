class EnemyDeathEffects:
    def __init__(self, enemy):
        self.enemy = enemy
        self.cleanup_started = False
        self.visual_started = False

        self.particle_preset = 'enemy_death_burst'
        self.particle_colour = [255, 255, 255, 255]
        self.particle_count = 30

        self.kill_sound_key = 'killed'
        self.kill_sound_volume = 0.25
        self.dead_sound_key = 'dead'
        self.dead_sound_volume = 0.7

        self.effect = 'alpha'
        self.alpha = 255
        self.alpha_fade_rate = 0.95
        self.alpha_kill_threshold = 5

        self.dissolve_colour = [1, 1, 1, 1]
        self.dissolve_size = 0.18
        self.dissolve_duration = 100

    def begin_cleanup(self):
        if self.cleanup_started:
            return False

        self.cleanup_started = True
        self.enemy.flags['attack_able'] = False
        self.enemy.flags['hurt_able'] = False
        self.enemy.velocity = [0, 0]
        return True

    def play_kill_sound(self):
        self._play_sound(self.kill_sound_key, self.kill_sound_volume)

    def play_dead_sound(self):
        self._play_sound(self.dead_sound_key, self.dead_sound_volume)

    def _play_sound(self, sound_key, volume):
        self.enemy.game_objects.sound.play_enemy_sound(self.enemy, sound_key, volume=volume)

    def emit_particles(self):
        self.enemy.game_objects.particles.emit(
            self.particle_preset,
            pos=self.enemy.hitbox.center,
            n=self.particle_count,
            colour=self.particle_colour,
        )

    def start_visual(self):
        if self.visual_started:
            return False

        self.visual_started = True
        if self.effect == 'dissolve':
            self.enemy.shader_state.enter_state(
                'Dissolve',
                colour=self.dissolve_colour,
                size=self.dissolve_size,
                duration=self.dissolve_duration,
                on_complete=self.enemy.kill,
            )
            return True

        self.enemy.shader_state.enter_state(
            'Alpha',
            alpha=self.alpha,
            fade_rate=self.alpha_fade_rate,
            kill_threshold=self.alpha_kill_threshold,
            on_complete=self.enemy.kill,
        )
        return True

class ShadowEnemyDeathEffect(EnemyDeathEffects):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.particle_colour = [0, 0, 0, 255]
        self.alpha_fade_rate = 0.95
