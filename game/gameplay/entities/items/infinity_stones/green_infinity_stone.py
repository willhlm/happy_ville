import pygame
from engine.utils import read_files
from gameplay.entities.items.base.item_definition import ItemDefinition
from gameplay.entities.items.infinity_stones.base_infinity_stone import InfinityStones

class GreenInfinityStone(InfinityStones):#faster slash (changing framerate)
    item_definition = ItemDefinition(
        description='fast sword swings',
    )

    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = GreenInfinityStone.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.colour = {'green':[105,139,105,255]}
        self.interact_component.apply_spawn()

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/infinity_stones/green/',game_objects)#for inventory
        super().pool(game_objects)

    @classmethod
    def entry_on_attach(cls, entry, player):
        player.sword.modifier_manager.add_modifier('green_stone')
