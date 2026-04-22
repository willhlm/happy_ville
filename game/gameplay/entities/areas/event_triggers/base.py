import pygame

from ..base import BaseArea


class EventTrigger(BaseArea):
    blocks_on_flow_complete = True
    blocks_on_event_complete = False

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.event = kwarg.get('event', False)
        self.ID = kwarg.get('ID', False)
        self.kwarg = kwarg

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return

        if self.ID and self.game_objects.world_state.narrative.is_flow_complete(self.ID):
            self.kill()
            return

        if self.game_objects.registry.fetch('sequences', self.event):
            self.game_objects.sequence_manager.start_sequence(self.event, **self.kwarg)
        elif self._is_registered_state():
            self.game_objects.game.state_manager.enter_state(self.event, **self.kwarg)
        else:
            self.game_objects.quests_events.initiate_event(self.event)

        self.kill()

    def _is_registered_state(self):
        return self.game_objects.game.state_manager.has_state(self.event)

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('ID', kwarg['event'])
