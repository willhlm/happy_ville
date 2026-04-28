import pygame

class Image():
    def __init__(self, game_objects, image, position, size):
        self.game_objects = game_objects
        self.image = image
        self.rect = pygame.Rect(position, [size[0], size[1]])
    
    def render(self, target):        
        image_width, image_height = self.image.size
        position = (int(self.rect.x + (self.rect.width - image_width) * 0.5), int(self.rect.y + (self.rect.height - image_height) * 0.5))
        self.game_objects.game.display.render(self.image, target, position = position)

    def on_enter(self):
        pass

    def active(self):
        pass

    def on_exit(self):
        pass
