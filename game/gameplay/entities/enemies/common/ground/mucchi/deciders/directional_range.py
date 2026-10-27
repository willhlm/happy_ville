from gameplay.entities.enemies.common.shared.state_machine.deciders.config_utils import resolve_distance
from gameplay.entities.enemies.common.shared.state_machine.deciders.decision import Decision


class DirectionalRangeDecider:
    """Transition when the player enters or leaves a surface-facing zone."""

    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.config = kwargs
        self.distance = resolve_distance(entity, kwargs, 'ready')

    def choose(self, player_distance, dt):
        player_is_inside = self._player_is_inside(player_distance)
        should_transition = player_is_inside
        if self.config.get('condition', 'inside') == 'outside':
            should_transition = not player_is_inside

        if not should_transition:
            return []

        return [Decision(
            next_state=self.config['next_state'],
            score=self.config['score'],
            priority=self.config['priority'],
            kwargs=self.config.get('kwargs', {}),
        )]

    def _player_is_inside(self, player_distance):
        outward = self.entity.attack_vector
        forward_distance = (
            player_distance[0] * outward[0]
            + player_distance[1] * outward[1]
        )
        sideways_distance = abs(
            player_distance[0] * -outward[1]
            + player_distance[1] * outward[0]
        )
        reach, half_width = self.distance

        return (
            0 <= forward_distance <= reach
            and sideways_distance <= half_width
        )
