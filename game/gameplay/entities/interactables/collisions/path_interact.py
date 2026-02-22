import pygame
from .base_collisions import BaseCollisions

class PathInteract(BaseCollisions):
    def __init__(self, pos, game_objects, size, destination, spawn, image):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def interact(self):
        self.game_objects.player.reset_movement()
        self.game_objects.player.currentstate.enter_state('Idle_main')#infstaed of idle, should make her move a little dependeing on the direction
        self.game_objects.map.load_map(self.game_objects.game.state_manager.state_stack[-1],self.destination, self.spawn)

