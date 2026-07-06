from .base import EventTrigger


class GameplayEventTrigger(EventTrigger):
    blocks_on_event_complete = True

    def activate(self):
        self.game_objects.quests_events.initiate_event(self.key)
        return True

    def is_complete(self):
        return self.game_objects.world_state.narrative.is_event_complete(self.key)

    @classmethod
    def get_event_completion_key(cls, kwarg):
        return kwarg["key"]
