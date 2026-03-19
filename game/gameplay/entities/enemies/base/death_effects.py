class EnemyDeathEffects:
    def __init__(self, enemy):
        self.enemy = enemy
        self.cleanup_started = False
        
        self.particle_preset = 'enemy_death_burst'
        self.particle_colour = [255, 255, 255, 255]
        self.particle_count = 30

        self.effect = 'alpha'
        self.alpha = 255
        self.alpha_fade_rate = 0.82
        self.alpha_kill_threshold = 8

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

    def emit_particles(self):
        self.enemy.game_objects.particles.emit(
            self.particle_preset,
            pos=self.enemy.hitbox.center,
            n=self.particle_count,
            colour=self.particle_colour,
        )

    def start_visual(self):
        if self.effect == 'dissolve':
            self.enemy.shader_state.enter_state(
                'Dissolve',
                colour=self.dissolve_colour,
                size=self.dissolve_size,
                duration=self.dissolve_duration,
                on_complete=self.enemy.kill,
            )
            return

        self.enemy.shader_state.enter_state(
            'Alpha',
            alpha=self.alpha,
            fade_rate=self.alpha_fade_rate,
            kill_threshold=self.alpha_kill_threshold,
            on_complete=self.enemy.kill,
        )
