import pygame
from engine.utils import read_files
from gameplay.entities.items.infinity_stones.base_infinity_stone import InfinityStones

class PurpleInfinityStone(InfinityStones):#reflect projectile -> crystal caves
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = PurpleInfinityStone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'purple':[154,50,205,255]}
        self.description = 'reflects projectiels'

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/infinity_stones/purple/',game_objects)#for inventory
        super().pool(game_objects)

    def attach(self, player):
        player.sword.stone_states['projectile_collision'].enter_state('Projectile_collision', 'projectile_collision')