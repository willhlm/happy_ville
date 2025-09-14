import pygame
from engine.utils import read_files
from gameplay.entities.items.infinity_stones.base_infinity_stone import InfinityStones

class OrangeInfinityStone(InfinityStones):#bigger hitbox
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = OrangeInfinityStone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'orange':[255,127,36,255]}
        self.description = 'larger hitbox'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/enteties/items/infinity_stones/orange/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y, 80, 40)
        self.sword.hitbox = self.sword.rect.copy()