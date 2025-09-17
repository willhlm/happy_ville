import pygame
from engine.utils import read_files
from engine.system import animation
from .base_texture import BaseTexture
from gameplay.entities.shared.states import states_basic

class SeedPlatform(BaseTexture):
    def __init__(self, arrow, game_objects, dir):
        super().__init__(arrow.hitbox.center, game_objects)
        self.lifetime = 200
        self.sprites = SeedPlatform.sprites
        self.image = self.sprites['grow'][0]

        self.animation = animation.Animation(self)        
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name = 'grow')

        self.get_hitbox(arrow, dir)

    def update(self, dt):
        super().update(dt)
        self.lifetime -= dt
        if self.lifetime < 0:
            self.kill()

    def release_texture(self):#called when .kill() and empty group
        pass

    def pool(game_objects):
        SeedPlatform.sprites = read_files.load_sprites_dict('assets/sprites/animations/seeds/platform/', game_objects)

    def get_hitbox(self, arrow, dir):
        if dir == [-1, 0]:#left
            self.angle = 90
            pos = [arrow.hitbox.midleft[0], arrow.hitbox.bottomleft[1] - self.image.height * 0.5]
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.height, self.image.width )
        elif dir == [1, 0]:#right
            self.angle = -90
            pos = [arrow.hitbox.midright[0] - self.image.width, arrow.hitbox.topright[1]]
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.height, self.image.width )
        elif dir == [0, -1]:#down
            self.angle = 0
            pos = [arrow.hitbox.midleft[0], arrow.hitbox.midleft[1] - self.image.height + arrow.hitbox[3] * 0.5]
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.width , self.image.height)
        elif dir == [0, 1]:#up
            self.angle = 180
            pos = arrow.hitbox.topleft
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

        self.rect = self.hitbox.copy()

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, angle = self.angle, position = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])))#int seem nicer than round