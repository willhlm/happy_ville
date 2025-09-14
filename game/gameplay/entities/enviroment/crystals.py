import pygame
from gameplay.entities.enviroment.base.layered_objects import LayeredObjects

class Crystals(LayeredObjects):
    def __init__(self, pos, game_objects, parallax, layer_name, crystal_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name,live_blur)  
        self.init_sprites('assets/sprites/animations/crystals/' + crystal_name + '/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.shader = game_objects.shaders['highlight']  
        
        self.speed = 2
        self.shine_progress = 0

    def update(self, dt):
        super().update(dt)  
        if self.shine_progress * self.speed >= 1:
            if random.randint(0,500) == 0: self.shine_progress = 0                    
        else:
            self.shine_progress += 0.01 * dt

    def draw(self, target):
        self.shader['shine_progress'] = self.shine_progress
        self.shader['speed'] = self.speed
        super().draw(target)