import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class HealthBar(AnimatedEntity):
    def __init__(self,entity):
        super().__init__(entity.rect.center,entity.game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/hud/health_bar/',entity.game_objects)
        self.entity = entity#the boss
        self.max_health = entity.health
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.width = self.rect[2]
        self.rect.topleft = [self.game_objects.game.window_size[0]*0.5 - self.width*0.5,3]

    def resize(self):#in principle, should just be called when boss take dmg
        width = max(self.width * (self.entity.health/self.max_health),0)
        for index, sprite in  enumerate(self.sprites['idle']):
            self.sprites['idle'][index] = pygame.transform.scale(sprite,[width,self.rect[3]])
