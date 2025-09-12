import pygame 
from gameplay.entities.interactables.base.interactables import Interactables

class Safe_spawn(Interactables):#area which gives the coordinates which will make aila respawn at after falling into a hole
    def __init__(self, pos, game_objects, size, position):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.position = position

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update_render(self, dt):
        pass

    def update(self, dt):
        self.group_distance()

    def player_collision(self, player):
        player.backpack.map.save_safespawn(self.position)

