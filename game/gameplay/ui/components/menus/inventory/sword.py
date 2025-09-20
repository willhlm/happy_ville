import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Sword(AnimatedEntity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/menus/inventory/sword/',game_objects)#for inventory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos

    def set_level(self, level):
        self.currentstate.set_animation_name('level_'+str(level))

#radna inventory screen
