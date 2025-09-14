import pygame
from engine.utils import read_files
from .base_shadow_light import BaseShadowLight

class DarkForest_1(BaseShadowLight):#a platform which dissapears when there is no light
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/block/light_interaction/dark_forest_1/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.cut_rect = pygame.Rect(pos[0], pos[1], self.image.size[0], self.image.size[1])
        self.lights = game_objects.game.display.make_layer(self.image.size)

    def update(self, dt):
        self.check_light()
