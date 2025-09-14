import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files

class Projectile_1(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = Projectile_1.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.lifetime = kwarg.get('lifetime', 200)
        self.dir = kwarg.get('dir', [1, 0])
        amp = kwarg.get('amp', [5, 5])
        self.velocity = [amp[0] * self.dir[0], amp[1] * self.dir[1]]

    def pool(game_objects):
        Projectile_1.sprites = read_files.load_sprites_dict('assets/sprites/attack/projectile_1/',game_objects)

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)

    def update_vel(self, dt):
        self.velocity[1] += 0.05 * dt#gravity

    def collision_platform(self,platform):
        self.flags['aggro'] = False
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.collision_platform(None)

    def take_dmg(self, dmg):#called when fprojicle collides
        self.collision_platform(None)
