from gameplay.entities.base.entity_overlap import EntityOverlap


class JetBurstLaunchArea(EntityOverlap):
    """Temporary JetBurst volume that launches each overlapping entity once."""

    def __init__(self, rect, game_objects, source, launch_speed, duration):
        super().__init__(rect, game_objects)
        self.source = source
        self.launch_speed = abs(float(launch_speed))
        self.duration = float(duration)
        self._launched_entities = set()

    def update(self, dt):
        if not self.source.functional:
            self.kill()
            return

        self.duration -= dt
        if self.duration <= 0:
            self.kill()

    def collision(self, entity):
        if entity in self._launched_entities:
            return

        movement_modifier = getattr(entity, 'movement_modifier', None)
        if movement_modifier is None:
            return

        movement_modifier.add_modifier(
            'jet_burst_launch',
            priority=100,
            entity=entity,
            launch_speed=self.launch_speed,
        )
        self._launched_entities.add(entity)

