from .base import EventTrigger


class UIOverlay(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.overlay_key = kwarg.get("overlay")
        self.game_objects.ui.overlay.preload_dynamic_overlay(self.game_objects, self.overlay_key)

    def on_collision(self, entity):
        if type(entity).__name__ != "Player":
            return

        if self.ID and self.game_objects.world_state.narrative.is_flow_complete(self.ID):
            self.kill()
            return

        self.game_objects.ui.overlay.play_dynamic_overlay(self.game_objects, self.overlay_key)

        self.game_objects.world_state.narrative.mark_flow_complete(self.get_completion_key(self.kwarg))
        self.kill()

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get("ID", kwarg.get("overlay") or kwarg.get("overlay_key") or kwarg.get("data") or kwarg["event"])
