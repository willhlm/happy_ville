import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class LogoLoading(AnimatedEntity):
    def __init__(self, game_objects):
        super().__init__([500,300], game_objects)
        self.sprites = LogoLoading.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.animation.framerate = 0.1#makes it slower

    def pool(game_objects):
        LogoLoading.sprites = read_files.load_sprites_dict('assets/sprites/ui/hud/logo_loading/',game_objects)

    def update(self, dt):
        super().update(dt)
        self.rect.topleft = [self.true_pos[0] + self.game_objects.camera_manager.camera.scroll[0], self.true_pos[1] + self.game_objects.camera_manager.camera.scroll[1]]

    def release_texture(self):
        pass

    def reset_timer(self):
        self.kill()
