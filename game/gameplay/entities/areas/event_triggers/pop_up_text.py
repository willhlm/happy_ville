from .base import EventTrigger
from ..triggers import WorldTextTrigger


class PopUpTextTrigger(EventTrigger):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects, size, **kwarg)
        self.pos = pos
        self.size = size


    def activate(self):
        kwargs = {'text': self.key,
                  'non_col': True,
                  'kill_con': 'drop_down'}
        self.game_objects.interactables.add(
            WorldTextTrigger(
                self.pos,
                self.game_objects,
                self.size,
                **kwargs
            )
        )
        return True

    def should_mark_complete(self):
        return True
