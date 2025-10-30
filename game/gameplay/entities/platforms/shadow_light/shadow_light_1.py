import pygame
from engine.utils import read_files
from .base_shadow_light import BaseShadowLight

class ShadowLight_1(BaseShadowLight):#collsion block but only lights and interacts when there is light overlap
    def __init__(self, pos, game_objects, size):
        super().__init__(pos, game_objects)
        self.size = size

        self.empty = game_objects.game.display.make_layer(size)
        self.image_layer = game_objects.game.display.make_layer(size)
        self.lights = game_objects.game.display.make_layer(size)

        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.cut_rect = self.rect.copy()  # A rectangle used to cut out light sources for shader
        self.hitbox = self.rect.copy()  # The initial hitbox of the platform
        self.time = 0

        self.game_objects.shaders['rectangle_border']['screenSize'] = self.game_objects.game.window_size

    def update_render(self, dt):                
        pass

    def update(self, dt):
        self.check_light()  # Check if the platform is hit by light
        self.time += dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['rectangle_border']['TIME'] = self.time
        self.game_objects.game.display.render(self.empty.texture, self.image_layer, shader=self.game_objects.shaders['rectangle_border'])#make the rectangle
        self.image = self.image_layer.texture
        super().draw(target)

    def release_texture(self):#called when .kill() and empty group
        self.image.release()
        self.image_layer.release()
        self.empty.release()
        self.lights.release()
        self.platforms = []
