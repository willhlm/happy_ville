import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files

class PoisonBlob(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = PoisonBlob.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 100)
        self.dir = kwarg.get('dir', [1, -1])
        amp = kwarg.get('amp', [5, 5])
        self.velocity = [-amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)

    def update_vel(self, dt):
        self.velocity[1] += 0.1 * dt#graivity

    def take_dmg(self, dmg):#aila sword without purple stone
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def collision_platform(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def pool(game_objects):
        PoisonBlob.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/poisonblobb/', game_objects)
