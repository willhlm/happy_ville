from .base import EventTrigger


class Narration(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.narration_key = kwarg["key"]
        self.game_objects.ui.overlay.preload_narration(self.narration_key)

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player':
            return

        narration = self.game_objects.ui.overlay.get_narration(self.narration_key)

        self.game_objects.ui.overlay.play_text_block(
            self.game_objects,
            lines=narration["lines"],
            mode=narration.get("mode", "block"),
            sound=narration.get("sound"),
            channel="narration",
        )

        self.game_objects.world_state.narrative.mark_flow_complete(self.get_completion_key(self.kwarg))
        self.kill()

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('ID', kwarg["key"])
