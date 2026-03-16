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
        if self.game_objects.transition.is_busy:
            return
        self.player_transport(entity)
        entity.take_dmg(damage = 1)

    def player_transport(self, player):#transports the player to safe position
        if player.health > 1:#if about to die, don't transport to safe point
            player.currentstate.enter_state('invisible')
            self.game_objects.transition.run(
                previous_state=self.game_objects.game.state_manager.state_stack[-1],
                style="fade_black",
                action=lambda: self._move_player_to_safe_spawn(player),
                after=lambda: player.currentstate.handle_input('pray_post'),
                fade_length=60,
            )
        player.velocity = [0,0]
        player.acceleration = [0,0]

    def _move_player_to_safe_spawn(self, player):
        player.reset_movement()
        player.set_pos(player.backpack.map.spawn_point['safe_spawn'])
        player.currentstate.enter_state('crouch', phase='main')
