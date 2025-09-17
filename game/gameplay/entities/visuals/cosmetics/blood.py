import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Blood(AnimatedEntity):
    def __init__(self, pos, game_objects, dir = [1,0]):
        super().__init__(pos, game_objects)
        self.sprites = Blood.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.dir = dir
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Blood.sprites = read_files.load_sprites_dict('assets/sprites/GFX/blood/death/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass
