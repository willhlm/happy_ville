from .decision import Decision


class SurfaceEdgeDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs

    def choose(self, player_distance, dt):
        surface_stick_physics = getattr(self.entity, "surface_stick_physics", None)
        if surface_stick_physics is None:
            return []

        lookahead = self.cfg.get(
            "lookahead",
            self.entity.config.get("movement", {}).get("surface_edge_lookahead", 6),
        )
        event = surface_stick_physics.get_blocked_edge_ahead(lookahead=lookahead)
        if event is None:
            return []

        if not self._matches(event):
            return []

        kwargs = dict(self.cfg.get("kwargs", {}))
        return [Decision(
            next_state=self.cfg["next_state"],
            score=self.cfg["score"],
            priority=self.cfg["priority"],
            kwargs=kwargs,
        )]

    def _matches(self, event):
        reasons = self.cfg.get("reasons")
        if reasons is not None and event.get("reason") not in reasons:
            return False

        from_sides = self.cfg.get("from_sides")
        if from_sides is not None and event.get("from_side") not in from_sides:
            return False

        to_sides = self.cfg.get("to_sides")
        if to_sides is not None and event.get("to_side") not in to_sides:
            return False

        return True
