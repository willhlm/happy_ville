import pygame
from engine.utils import read_files
from .base import RunningParticles

class Water(RunningParticles):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Water_running_particles.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)

    def reset_timer(self):
        self.kill()

    def pool(game_objects):#all things that should be saved in object pool
        Water.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/cosmetics/running_particles/water/', game_objects)

    def release_texture(self):#stuff that have pool shuold call this
        pass

