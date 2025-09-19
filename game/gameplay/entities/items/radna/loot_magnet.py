import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class LootMagnet(Radna):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = LootMagnet.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.description = 'Attracts loot ' + '[' + str(self.level) + ']'

    def equipped(self):#an update that should be called when equppied
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/radna/loot_magnet/',game_objects)#for inventory
        super().pool(game_objects)