import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class PrayEffect(AnimatedEntity):#the thing when aila pray
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = PrayEffect.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.center = pos

    def pool(game_objects):
        PrayEffect.sprites = read_files.load_sprites_dict('assets/sprites/animations/pray_effect/', game_objects)

    def spawn(self):
        pass

    def reset_timer(self):
        self.kill()

    def release_texture(self):
        pass
