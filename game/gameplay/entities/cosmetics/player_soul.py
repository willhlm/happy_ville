import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.states import states_basic

class PlayerSoul(AnimatedEntity):#the thing that popps out when player dies
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = PlayerSoul.sprites
        self.image = self.sprites['once'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name='once')

        self.timer = 0
        self.velocity = [0,0]

    def pool(game_objects):
        PlayerSoul.sprites = read_files.load_sprites_dict('assets/sprites/enteties/soul/', game_objects)

    def update(self, dt):
        super().update(dt)
        self.update_pos()
        self.timer += dt
        if self.timer > 100:#fly to sky
            self.velocity[1] = -20
        elif self.timer>200:
            self.kill()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0], self.true_pos[1] + self.velocity[1]]
        self.rect.topleft = self.true_pos

    def release_texture(self):
        pass
