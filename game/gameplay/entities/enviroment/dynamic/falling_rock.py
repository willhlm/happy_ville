import pygame
from .base_dynamic import BaseDynamic

class FallingRock(BaseDynamic):
    def __init__(self,pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.sprites = FallingRock.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.lifetime = 100

    def update(self):
        super().update()
        self.update_vel()
        self.destroy()

    def destroy(self):
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:
            self.kill()

    def update_vel(self):
        self.velocity[1] += 1
        self.velocity[1] = min(7,self.velocity[1])

    def pool(game_objects):#save the texture in memory for later use
        FallingRock.sprites = read_files.load_sprites_dict('assets/sprites/animations/falling_rock/rock/', game_objects)