from .base import EventTrigger


class UIOverlayTrigger(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.game_objects.ui.overlay.preload_dynamic_overlay(self.game_objects, self.key)

    def activate(self):
        self.game_objects.ui.overlay.play_dynamic_overlay(self.game_objects, self.key)
        return True

    def should_mark_complete(self):
        return True
