import pygame

from ..base import BaseArea


class PathCollision(BaseArea):
    is_path_collision = True

    def __init__(self, pos, game_objects, size, destination, spawn, entry_action):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn
        self.entry_action = entry_action

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def on_collision(self, player):
        sequences = self.game_objects.sequence_manager
        if sequences.is_active("map_traversal"):
            return
        sequences.start_sequence(
            "map_traversal",
            destination=self.destination,
            spawn=self.spawn,
            entry_action=self.entry_action,
            previous_state=self.game_objects.game.state_manager.state_stack[-1],
        )

    def on_noncollision(self, player):
        traversal = self.game_objects.sequence_manager.get_sequence("map_traversal")
        if traversal:
            traversal.path_cleared(self)
