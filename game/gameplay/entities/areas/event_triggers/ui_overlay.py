from .base import EventTrigger


class UIOVerlay(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.overlay = kwarg.get('overlay')

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player':
            return

        self.game_objects.ui.overlay.play_static_overlay(
            self.game_objects,
            overlay_key = self.overlay
        )

        self.game_objects.world_state.narrative.mark_flow_complete(self.get_completion_key(self.kwarg))
        self.kill()

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('text', kwarg.get('ID', kwarg['event']))
