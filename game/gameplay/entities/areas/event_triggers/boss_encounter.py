from .base import EventTrigger


class BossEncounterTrigger(EventTrigger):
    def activate(self):
        self.game_objects.sequence_manager.start_sequence(
            "boss_encounter",
            encounter=self.key,
        )
        return True

    def is_complete(self):
        return self.game_objects.world_state.narrative.is_boss_defeated(self.key)
