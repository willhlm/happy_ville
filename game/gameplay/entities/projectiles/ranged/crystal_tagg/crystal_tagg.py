import math
import pygame
from gameplay.entities.projectiles.base.platform_projectile import PlatformProjectile
from engine.utils import read_files
from .states import Idle

class CrystalTagg(PlatformProjectile):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.enable_surface_attachment()
        self.sprites = CrystalTagg.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.lifetime = kwarg.get('lifetime', 100)
        self.dir = kwarg.get('dir', [1, -1])
        amp = kwarg.get('amp', [5, 5])
        self.velocity = kwarg.get('velocity', [0.8 * amp[0] * self.dir[0], amp[1] * self.dir[1]])
        self.angle = self._get_trajectory_angle()
        self.currentstate = Idle(self)

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)
        self.angle = self._get_trajectory_angle()

    def update_vel(self, dt):
        if self.is_attached_to_surface():
            self.velocity[0] = 0
            self.velocity[1] = 0
            return
        self.velocity[1] += 0.1 * dt#graivity

    def _get_trajectory_angle(self):
        if self.velocity[0] == 0 and self.velocity[1] == 0:
            return getattr(self, 'angle', 0)
        return math.degrees(math.atan2(-self.velocity[0], self.velocity[1]))

    def draw(self, target):#called just before draw in group
        blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = blit_pos, angle = self.angle, shader = self.shader)

    def on_projectile_clash_lost(self, other):
        self.velocity = [0,0]
        self.currentstate.handle_input('death')

    def _collision_platform(self, collision):
        self.attach_to_surface(collision)
        self.velocity = [0,0]
        self.currentstate.handle_input('grow')

    def pool(game_objects):
        CrystalTagg.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/crystal_tagg/', game_objects)

    def handle_platform_collision(self, collision):
        self._collision_platform(collision)

    def destroy(self):
        if self.lifetime < 0:
            self.currentstate.handle_input('death')
