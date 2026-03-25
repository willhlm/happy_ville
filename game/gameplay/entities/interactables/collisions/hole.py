import pygame
from .base_collisions import BaseCollisions
from gameplay.entities.shared.components import hit_effects

class Hole(BaseCollisions):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.base_effect = hit_effects.create_contact_effect(game_objects, damage=1, hit_type='void', hitstop=40, knockback=[0, 0], attacker=self)
        self.base_effect.attacker_callbacks = {}

    def on_collision(self, entity):
        if self.game_objects.transition.is_busy:
            return
        self.player_transport(entity)
        effect = self.base_effect.copy()
        effect.meta['attacker_dir'] = [0, 0]
        entity.take_hit(effect)

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

    def _move_player_to_safe_spawn(self, player):
        player.reset_movement()
        player.set_pos(player.backpack.map.spawn_point['safe_spawn'])
        player.currentstate.enter_state('crouch', phase='main')
