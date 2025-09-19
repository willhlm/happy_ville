import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class HalfDamage(Radna):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = HalfDamage.sprites
        self.image = self.sprites[kwarg.get('state', 'idle')][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.level = 1
        self.description = 'Take half dmg ' + '[' + str(self.level) + ']'

    def attach(self):
        super().attach()
        self.entity.damage_manager.add_modifier('Half_dmg')

    def detach(self):
        super().detach()
        self.entity.damage_manager.remove_modifier('Half_dmg')

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/radna/half_dmg/',game_objects)#for inventory
        super().pool(game_objects)