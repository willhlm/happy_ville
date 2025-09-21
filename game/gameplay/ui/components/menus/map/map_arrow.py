import pygame, math
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class MapArrow(AnimatedEntity):#for invenotry, the pointer
    def __init__(self, pos, game_objects, map_text, direction):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/menus/map/arrow/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.time = 0
        self.map_text = map_text
        self.original_pos = pos

        if direction == 'left':
            self.angle = 0#angle of the arrow
            self.move_direction = [1,0]
        elif direction == 'right':
            self.angle = 180
            self.move_direction = [1,0]
        elif direction == 'up':
            self.angle = 90
            self.move_direction = [0,1]
        elif direction == 'down':
            self.angle = 270
            self.move_direction = [0,1]

    def activate(self):
        return self.map_text

    def update(self, dt):
        super().update(dt)
        self.time += dt * 0.1
        self.update_pos()

    def update_pos(self):
        self.rect.center = [self.rect.center[0] + 2 * self.move_direction[0] * math.sin(self.time), self.rect.center[1] + 2 * self.move_direction[1] * math.sin(self.time)]

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, angle = self.angle, position = self.rect.topleft)#shader render

    def reset(self):
        self.rect.topleft = self.original_pos
        self.time = 0

