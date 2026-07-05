from .base import EventTrigger


class NarrationTrigger(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.game_objects.ui.overlay.preload_narration(self.key)

    def activate(self):
        narration = self.game_objects.ui.overlay.get_narration(self.key)
        self.game_objects.ui.overlay.play_text_block(
            self.game_objects,
            lines=narration["lines"],
            mode=narration.get("mode", "block"),
            sound=narration.get("sound"),
            channel="narration",
        )
        return True

    def should_mark_complete(self):
        return True
