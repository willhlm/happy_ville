import random

from gameplay.entities.visuals.cosmetics.spirit_flash import SpiritFlash


class InteractionHintComponent:
    """Periodically highlights an entity and emits subtle ambient motes."""

    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.enabled = kwargs.get('interaction_hint', True)
        self.flash_interval = max(float(kwargs.get('interaction_hint_interval', 180)), 1.0)
        self.particle_interval = max(float(kwargs.get('interaction_particle_interval', 30)), 1.0)
        self._flash_timer = random.uniform(self.flash_interval * 0.5, self.flash_interval)
        self._particle_timer = random.uniform(0, self.particle_interval)

    def update(self, dt, active=True):
        if not self.enabled or not active:
            return

        self._flash_timer -= dt
        if self._flash_timer <= 0:
            self._flash_timer += self.flash_interval
            self._emit_flash()

        self._particle_timer -= dt
        if self._particle_timer <= 0:
            self._particle_timer += self.particle_interval
            self._emit_particle()

    def _emit_flash(self):
        self.entity.game_objects.cosmetics.add(
            SpiritFlash(
                self.entity.hitbox.center,
                self.entity.game_objects,
                size=(96, 96),
                radius=38,
                start_scale=0.25,
                end_scale=1.0,
                duration=32,
                alpha=110,
            )
        )

    def _emit_particle(self):
        rect = self.entity.hitbox
        position = (
            rect.centerx + random.uniform(-rect.width * 0.35, rect.width * 0.35),
            rect.centery + random.uniform(-rect.height * 0.2, rect.height * 0.2),
        )
        self.entity.game_objects.particles.emit('floaty_ambient', position, n=1)
