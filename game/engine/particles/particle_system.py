from gameplay.entities.visuals.particles.component_based.particle_presets import PRESETS

class ParticleSystem:
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def emit(self, preset_name: str, pos, n: int = 1, **overrides):
        preset_fn = PRESETS[preset_name]
        for _ in range(n):
            p = preset_fn(pos, self.game_objects,  **overrides)  # returns a Particle
            self.game_objects.cosmetics.add(p)
