import pygame
from gameplay.entities.base.static_entity import StaticEntity

class Beam(StaticEntity):
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size).texture
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.parallax = parallax
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.1

    def draw(self, target):
        self.game_objects.shaders['beam']['TIME'] = self.time
        pos = (int(self.true_pos[0]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1]-self.parallax[0]*self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = pos, shader = self.game_objects.shaders['beam'])#shader render