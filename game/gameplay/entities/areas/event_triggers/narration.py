from .base import EventTrigger


class Narration(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.start_index = int(kwarg.get('start_index', 0))
        self.count = int(kwarg.get('count', 2))
        self.text_key = kwarg.get('text', 'intro_lore')
        self.mode = kwarg.get('mode', 'sequential')

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player':
            return

        self.game_objects.ui.overlay.play_text_block(
            self.game_objects,
            self.text_key,
            start_index=self.start_index,
            count=self.count,
            mode=self.mode,
            channel="narration",
        )

        self.game_objects.world_state.narrative.mark_flow_complete(self.get_completion_key(self.kwarg))
        self.kill()

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('text', kwarg.get('ID', kwarg['event']))
