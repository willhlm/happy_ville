from .base import EventTrigger


class GauntletTrigger(EventTrigger):
    blocks_on_flow_complete = True

    def activate(self):
        self.game_objects.quests_events.initiate_event("gauntlet", ID=self.key)
        return True

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg["key"]
