import pygame
from engine.utils import read_files
from gameplay.entities.items.infinity_stones.base_infinity_stone import InfinityStones

class RedInfinityStone(InfinityStones):#more dmg
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = RedInfinityStone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'red':[255,64,64,255]}
        self.description = '10 procent more damage'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/red/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self):
        self.sword.dmg *= 1.1