from .base import EventTrigger


class SequenceTrigger(EventTrigger):
    def activate(self):
        self.game_objects.sequence_manager.start_sequence(self.key)
        return True
