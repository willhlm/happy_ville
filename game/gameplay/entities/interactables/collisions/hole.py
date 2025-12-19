import pygame
from gameplay.entities.interactables.base.interactables import Interactables

class Hole(Interactables):#area which will make aila spawn to safe_point if collided
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.bounds = [-800, 800, -800, 800]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.interacted = False

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.group_distance()
        #print(self.interacted, 'update')

    def update_render(self, dt):
        pass

    def collision(self, entity):
        if self.interacted: return#enter only once
        self.player_transport(entity)
        entity.take_dmg(damage = 1)
        self.interacted = True

    def player_transport(self, player):#transports the player to safe position
        if player.health > 1:#if about to die, don't transport to safe point
            self.game_objects.game.state_manager.enter_state(state_name = 'safe_spawn_1')
            player.currentstate.enter_state('invisible')
        player.velocity = [0,0]
        player.acceleration = [0,0]

    def noncollision(self, entity):#when player doesn't collide
        self.interacted = False        

