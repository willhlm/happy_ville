import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class ThunderSpark(AnimatedEntity):#when landing thunder dive
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = ThunderSpark.sprites
        self.image = self.sprites['death'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.currentstate = states_basic.Death(self)

    def pool(game_objects):
        ThunderSpark.sprites = read_files.load_sprites_dict('assets/sprites/animations/thunder_spark/', game_objects)

    def release_texture(self):
        pass
