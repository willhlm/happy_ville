from .base import EventTrigger


class QuestTrigger(EventTrigger):
    def activate(self):
        if self.game_objects.world_state.narrative.is_quest_completed(self.key):
            return False

        active_quest = self.game_objects.quests_events.get_active_quest(self.key)
        if active_quest is not None:
            if getattr(active_quest, "running", False):
                return False
            active_quest.initiate_quest()
            return True

        self.game_objects.quests_events.initiate_quest(self.key)
        return True

    def should_destroy(self):
        return False
