from .base import EventTrigger


class QuestEventTrigger(EventTrigger):
    def activate(self):
        self.game_objects.quests_events.initiate_event(self.trigger)
        return True

    def is_complete(self):
        return self.game_objects.world_state.narrative.is_event_complete(self.trigger)
