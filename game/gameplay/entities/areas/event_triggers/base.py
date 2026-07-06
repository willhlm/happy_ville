import pygame

from ..base import BaseArea


class EventTrigger(BaseArea):
    """Base class for map triggers.

    Available trigger names are currently:
    - narration: load narration content by key
    - ui_overlay: load overlay content by key
    - quest: start or resume a quest by key
    - pause_quest: pause an active quest by key
    - gauntlet: start the gauntlet event using key as its config id
    - boss_encounter: start the boss encounter sequence using key as its encounter id
    - event: start a gameplay event using key as its event id
    - sequence: start a sequence directly by key
    - state: enter a state directly by key
    """
    blocks_on_flow_complete = False
    blocks_on_event_complete = False

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.trigger = kwarg["trigger"]
        self.key = kwarg["key"]
        self.kwarg = dict(kwarg)

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def on_collision(self, entity):
        if type(entity).__name__ != "Player":
            return

        if self.is_complete():
            self.kill()
            return

        activated = self.activate()
        if not activated:
            return

        if self.should_mark_complete():
            self.game_objects.world_state.narrative.mark_flow_complete(self.get_completion_key(self.kwarg))

        if self.should_destroy():
            self.kill()

    def activate(self):
        raise NotImplementedError

    def is_complete(self):
        if not self.blocks_on_flow_complete:
            return False
        return self.game_objects.world_state.narrative.is_flow_complete(self.get_completion_key(self.kwarg))

    def should_mark_complete(self):
        return False

    def should_destroy(self):
        return True

    @classmethod
    def get_completion_key(cls, kwarg):
        return f"{kwarg['trigger']}:{kwarg['key']}"

    @classmethod
    def get_event_completion_key(cls, kwarg):
        return kwarg["trigger"]
