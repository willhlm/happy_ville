import pygame

from ..base import BaseArea

class BossEncounter(BaseArea):
    blocks_on_flow_complete = True

    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.hitbox = self.rect.copy()
        self.ID = kwarg.get('ID', False)
        self.kwarg = kwarg

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def on_collision(self, entity):
        if type(entity).__name__ != 'Player': return
        if self.ID and self.game_objects.world_state.narrative.is_boss_defeated(self.ID):
            self.kill()
            return

        if not self.game_objects.world_state.narrative.is_flow_complete(self.ID):
            self.game_objects.sequence_manager.start_sequence('boss_encounter', **self.kwarg)
        self.kill()

    @classmethod
    def get_completion_key(cls, kwarg):
        return kwarg.get('ID', 'boss_encounter')
