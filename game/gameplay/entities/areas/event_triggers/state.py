from .base import EventTrigger


class StateTrigger(EventTrigger):
    def activate(self):
        self.game_objects.game.state_manager.enter_state(self.key)
        return True
