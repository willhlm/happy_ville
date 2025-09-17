import pygame
from gameplay.entities.base.static_entity import StaticEntity

class FadeEffect(StaticEntity):#fade effect -> motion blue and fade
    def __init__(self, entity, **kwarg):
        super().__init__(entity.rect.center, entity.game_objects)
        self.image = entity.image
        self.image_copy = FadeEffect.image_copy

        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.center = entity.rect.center
        self.alpha = kwarg.get('alpha', 255)

        self.dir = entity.dir.copy()
        self.blur_dir = kwarg.get('blur_dir', [0.05, 0])

    def update_render(self, dt):
        self.alpha *= 0.9
        self.destroy()

    def draw(self, target):
        self.image_copy.clear(0,0,0,0)
        self.game_objects.shaders['motion_blur']['dir'] = self.blur_dir
        self.game_objects.shaders['motion_blur']['quality'] = 3
        self.game_objects.game.display.render(self.image, self.image_copy, shader = self.game_objects.shaders['motion_blur'])#shader render

        self.game_objects.shaders['alpha']['alpha'] = self.alpha
        blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image_copy.texture, target, position = blit_pos, flip = self.dir[0] > 0, shader = self.game_objects.shaders['alpha'])#shader render

    def pool(game_objects):
        size = (128, 80)#player canvas size
        FadeEffect.image_copy = game_objects.game.display.make_layer(size)

    def destroy(self):
        if self.alpha < 10:
            self.kill()

    def release_texture(self):
        pass        