import pygame


class ResultStamp:
    """A layout marker for the position of a dynamic option value."""

    def __init__(self, position, size):
        self.rect = pygame.Rect(position, size)
