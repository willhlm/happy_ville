import pygame
import math
import random
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.base.static_entity import StaticEntity

class Dusts(AnimatedEntity):#dust particles when doing things
    def __init__(self, pos, game_objects, dir = [1,0], state = 'one'):
        super().__init__(pos, game_objects)
        self.sprites = Dusts.sprites
        self.image = self.sprites[state][0]
        self.animation.play(state)
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.dir = dir
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Dusts.sprites = read_files.load_sprites_dict('assets/sprites/GFX/dusts/', game_objects, flip_x = True)

    def release_texture(self):#stuff that have pool shuold call this
        pass
