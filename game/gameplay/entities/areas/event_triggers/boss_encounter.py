from .base import EventTrigger
from gameplay.data.boss_encounter_configs import get_boss_encounter_config
from gameplay.entities.interactables.ability_ball.boss_reward_spawner import spawn_pending_boss_reward


class BossEncounterTrigger(EventTrigger):
    def __init__(self, pos, game_objects, size, **kwargs):
        super().__init__(pos, game_objects, size, **kwargs)
        self.spawn_pending_reward()

    def spawn_pending_reward(self):
        config = get_boss_encounter_config(self.key)
        boss_config = config.get('boss', {})
        boss_id = boss_config.get('id', self.key)
        boss_class = boss_config.get('class')
        if boss_class is not None:
            spawn_pending_boss_reward(
                self.game_objects, boss_id, boss_class, self.hitbox.center
            )

    def activate(self):
        self.game_objects.sequence_manager.start_sequence(
            "boss_encounter",
            encounter=self.key,
        )
        return True

    def is_complete(self):
        return self.game_objects.world_state.narrative.is_boss_defeated(self.key)
