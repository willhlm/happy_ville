import pygame
from engine.utils import read_files
from gameplay.entities.items.infinity_stones.base_infinity_stone import InfinityStones

class GreenInfinityStone(InfinityStones):#faster slash (changing framerate)
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = GreenInfinityStone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'green':[105,139,105,255]}
        self.description = 'fast sword swings'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/infinity_stones/green/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self, player):
        player.sword.stone_states['slash'].enter_state('Slash', 'slash')