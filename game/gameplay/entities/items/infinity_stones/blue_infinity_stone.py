import pygame
from engine.utils import read_files
from gameplay.entities.items.infinity_stones.base_infinity_stone import InfinityStones

class BlueInfinityStone(InfinityStones):#get spirit at collision
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = BlueInfinityStone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'blue':[0,0,205,255]}
        self.description = 'add spirit to the swinger'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/blue/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self, player):
        player.sword.stone_states['enemy_collision'].enter_state('Enemy_collision', 'enemy_collision')