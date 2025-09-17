import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Twinkle(AnimatedEntity):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Twinkle.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

    def reset_timer(self):
        super().reset_timer()
        self.kill()

    def release_texture(self):
        pass

    def pool(game_objects):
        Twinkle.sprites = read_files.load_sprites_dict('assets/sprites/GFX/twinkle/', game_objects)
