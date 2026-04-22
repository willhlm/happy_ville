import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class HalfDamage(Radna):
    inventory_level = 1
    inventory_description = 'Take half dmg [1]'

    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = HalfDamage.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.interact_component.apply_spawn()

    @classmethod
    def entry_on_attach(cls, entry):
        entry.owner.damage_manager.add_modifier('Half_dmg')

    @classmethod
    def entry_on_detach(cls, entry):
        entry.owner.damage_manager.remove_modifier('Half_dmg')

    @classmethod
    def pool(cls, game_objects):
        cls.sprites = read_files.load_sprites_dict('assets/sprites/entities/items/radna/half_dmg/',game_objects)#for inventory
        super().pool(game_objects)
