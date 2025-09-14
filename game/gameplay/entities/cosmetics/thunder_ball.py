import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class ThunderBall(AnimatedEntity):#for thunder dive
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = ThunderBall.sprites
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name='once')

    def pool(game_objects):
        ThunderBall.sprites = read_files.load_sprites_dict('assets/sprites/enteties/soul/', game_objects)

    def release_texture(self):
        pass
