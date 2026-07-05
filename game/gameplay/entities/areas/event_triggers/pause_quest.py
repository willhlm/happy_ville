from .base import EventTrigger


class PauseQuestTrigger(EventTrigger):
    def activate(self):
        active_quest = self.game_objects.quests_events.get_active_quest(self.key)
        if active_quest is None or not getattr(active_quest, "running", False):
            return False

        self.game_objects.quests_events.pause_quest(self.key)
        return True

    def should_destroy(self):
        return False
