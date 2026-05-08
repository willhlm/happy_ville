from gameplay.entities.enemies.common.shared.state_machine.deciders.decision import Decision


class CheckPlayerCrossOverDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.cfg = kwargs

    def choose(self, player_distance, dt):
        player_on_facing_side = (
            (player_distance[0] >= 0 and self.entity.dir[0] == 1)
            or (player_distance[0] < 0 and self.entity.dir[0] == -1)
        )

        if not player_on_facing_side:
            return []

        return [
            Decision(
                next_state=self.cfg["next_state"],
                score=self.cfg["score"],
                priority=self.cfg["priority"],
                kwargs=self.cfg.get("kwargs", {}),
            )
        ]
