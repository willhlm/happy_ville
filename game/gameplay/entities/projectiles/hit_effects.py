class HitEffect():
    def __init__(self, sound, particles, hitstop = 10, knockback = (25, 10)):
        self.hitstop = hitstop
        self.knockback = knockback
        self.particles = particles
        self.sound = sound

    def apply(self, sword, enemy):
        """Apply effects when the sword hits an enemy."""
        # Hitstop
        sword.entity.hitstop_states.enter_state('Stop', lifetime = self.hitstop)
        enemy.apply_hitstop(lifetime = self.hitstop, call_back = {'knock_back': {'amp':self.knockback, 'dir':sword.dir}})

        # Particles
        enemy.emit_particles(**self.particles)
        sword.clash_particles(enemy.hitbox.center, number_particles=5)

        # Sound
        sword.game_objects.sound.play_sfx(self.sound, vol=0.3)     