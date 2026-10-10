import pygame
from ..base import BaseArea

class PathInteract(BaseArea):
    def __init__(self, pos, game_objects, size, **kwargs):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

        self.destination = kwargs.get("path_to")
        self.destination_area = self.destination[:self.destination.rfind('_')]
        self.spawn = kwargs.get("spawn")
        self.departure_action = kwargs.get("departure_action", "idle")
        self.arrival_action = kwargs.get("arrival_action", "idle")
        self.arrival_lock_time = kwargs.get("arrival_lock_time", 0)

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def interact(self, player=None):
        if self.game_objects.transition.is_busy:
            return
        self.game_objects.sequence_manager.start_sequence(
            "map_traversal",
            destination=self.destination,
            spawn=self.spawn,
            departure_action=self.departure_action,
            arrival_action=self.arrival_action,
            arrival_lock_time=self.arrival_lock_time,
            wait_for_arrival_path_clear=False,
            previous_state=self.game_objects.game.state_manager.state_stack[-1],
        )
