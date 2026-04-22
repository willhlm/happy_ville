import pygame, random
from gameplay.entities.projectiles.base.platform_projectile import PlatformProjectile
from engine.utils import read_files

class BouncyBalls(PlatformProjectile):#for ball challange room
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = BouncyBalls.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.light = game_objects.lights.add_light(self)
        self.velocity = [random.uniform(-2,2),random.uniform(-2,-1)]

    def pool(game_objects):
        BouncyBalls.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/projectile_1/',game_objects)

    def release_texture(self):
        pass

    def kill(self):#when lifeitme runs out or hit by aila sword
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    def on_projectile_clash_lost(self, other):#when hit by aila sword without purple stone
        self.velocity = [0,0]
        self.dmg = 0
        self.currentstate.handle_input('Death')
        self.game_objects.signals.emit('ball_killed')

    def handle_platform_collision(self, collision):
        if collision.axis == 'x':
            self.currentstate.handle_input(collision.collision_kind)
            self.velocity[0] = -self.velocity[0]
            return

        self.velocity[1] = -self.velocity[1]
