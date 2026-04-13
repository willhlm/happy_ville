class VoidHazardComponent:
    def __init__(self, owner):
        self.owner = owner
        self.game_objects = owner.game_objects

    def trigger(self, entity, after_transport=None, attacker=None):
        if self.game_objects.transition.is_busy:
            return

        attacker = attacker or self.owner
        if hasattr(entity, "hazard_resolver"):
            entity.hazard_resolver.handle_void(attacker, after_transport=after_transport)
            return

        if hasattr(entity, "currentstate") and hasattr(entity.currentstate, "die"):
            entity.currentstate.die()
            return

        if hasattr(entity, "kill"):
            entity.kill()
