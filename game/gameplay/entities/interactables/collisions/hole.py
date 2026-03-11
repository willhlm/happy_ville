import pygame
from .base_collisions import BaseCollisions

class Hole(BaseCollisions):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen

    def on_collision(self, entity):
        self.player_transport(entity)
        entity.take_dmg(damage = 1)

    def player_transport(self, player):#transports the player to safe position
        if player.health > 1:#if about to die, don't transport to safe point
            self.game_objects.game.state_manager.enter_state(state_name = 'safe_spawn_1')
            player.currentstate.enter_state('invisible')
        player.velocity = [0,0]
        player.acceleration = [0,0]    