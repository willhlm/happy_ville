import random

from gameplay.entities.base.static_entity import StaticEntity


class ParticleEmitterEffect(StaticEntity):
    """A non-rendering cosmetic actor that emits a particle preset at an interval."""

    def __init__(
        self,
        pos,
        game_objects,
        *,
        preset,
        interval=1,
        particle_count=1,
        position_jitter=(0, 0),
        **particle_kwargs,
    ):
        super().__init__(pos, game_objects)
        self.pos = list(pos)
        self.preset = preset
        self.interval = max(float(interval), 0.001)
        self.particle_count = int(particle_count)
        self.position_jitter = list(position_jitter)
        self.particle_kwargs = particle_kwargs
        self.time_until_emit = self.interval
        self.always_active = True
        self._emit()

    def _emit(self):
        position = [
            self.pos[0] + random.uniform(-self.position_jitter[0], self.position_jitter[0]),
            self.pos[1] + random.uniform(-self.position_jitter[1], self.position_jitter[1]),
        ]
        self.game_objects.particles.emit(
            self.preset,
            position,
            n=self.particle_count,
            **self.particle_kwargs,
        )

    def update(self, dt):
        self.time_until_emit -= dt
        while self.time_until_emit <= 0:
            self._emit()
            self.time_until_emit += self.interval

    def draw(self, target):
        pass
