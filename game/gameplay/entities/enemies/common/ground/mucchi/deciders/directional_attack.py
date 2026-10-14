from gameplay.entities.enemies.common.shared.state_machine.deciders.config_utils import resolve_distance
from gameplay.entities.enemies.common.shared.state_machine.deciders.decision import Decision


class DirectionalAttackDecider:
    """Attack only when the player is in front of Mucchi's surface."""

    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.config = kwargs
        self.attack_distance = resolve_distance(entity, kwargs, 'attack')

    def choose(self, player_distance, dt):
        outward = self.entity.attack_vector
        forward_distance = (
            player_distance[0] * outward[0]
            + player_distance[1] * outward[1]
        )
        sideways_distance = abs(
            player_distance[0] * -outward[1]
            + player_distance[1] * outward[0]
        )
        reach, half_width = self.attack_distance

        if forward_distance < 0 or forward_distance > reach:
            return []
        if sideways_distance > half_width:
            return []
        if self.entity.currentstate.cooldowns.get(self.config['cooldown']) > 0:
            return []

        return [Decision(
            next_state=self.config['next_state'],
            score=self.config['score'],
            priority=self.config['priority'],
            kwargs=self.config.get('kwargs', {}),
        )]
