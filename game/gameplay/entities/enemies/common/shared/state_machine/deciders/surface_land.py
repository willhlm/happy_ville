from .decision import Decision


class SurfaceLandDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs

    def choose(self, player_distance, dt):
        consume_event = getattr(self.entity, "consume_surface_landing_event", None)
        if consume_event is None:
            return []

        event = consume_event()
        if event is None:
            return []

        min_air_time = self.cfg.get("min_air_time")
        if min_air_time is not None and event.get("air_time", 0) < min_air_time:
            return []

        return [Decision(
            next_state=self.cfg["next_state"],
            score=self.cfg["score"],
            priority=self.cfg["priority"],
            kwargs=dict(self.cfg.get("kwargs", {})),
        )]
