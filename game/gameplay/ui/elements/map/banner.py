import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Banner(AnimatedEntity):
    def __init__(self, pos, game_objects, type, map_text):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/map/banner/banner_' + type + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.rect.topleft = pos
        self.original_pos = pos
        self.map_text = map_text
        self.time = 0#for the animation
        #self.blit_text(map_text)

    def blit_text(self,text):
        screen = self.game_objects.game.display.make_layer((self.image.width,self.image.height))#make a layer ("surface")
        text_surface = self.game_objects.font.render(text = text)
        for state in self.sprites.keys():
            for frame, image in enumerate(self.sprites[state]):
                self.game_objects.game.display.render(image, screen)
                self.game_objects.game.display.render(text_surface, screen, position = (image.width*0.5,image.height*0.5))
                self.sprites[state][frame] = screen

    def update_scroll(self, scroll):
        self.rect.center = [self.rect.center[0] + scroll[0], self.rect.center[1] + scroll[1]]

    def update(self, dt):
        super().update(dt)
        self.time += dt * 0.05
        self.update_pos()

    def update_pos(self):
        self.rect.center = [self.rect.center[0], self.rect.center[1] + math.sin(2 * self.time)]

    def activate(self):#called from map when selecting the pecific banner
        return self.map_text

