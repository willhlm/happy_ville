import pygame, math
from gameplay.entities.projectiles.base.platform_projectile import PlatformProjectile
from engine.utils import read_files
from . import seed_spawner

class Arrow(PlatformProjectile):#should it be called seed?
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Arrow.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100

        self.dir = kwarg.get('dir', [1, 0])
        normalise = (self.dir[0] ** 2 + self.dir[1] ** 2)**0.5
        amp = kwarg.get('time', 0)/50#50 is the charge duration, how long one sohuld press to reach max speed
        amp = min(amp, 1)#limit the max charge to 1

        self.velocity = [amp * self.dir[0] * 20 / normalise, amp * self.dir[1] * 20 / normalise]
        self.seed_spawner = seed_spawner.SeedSpawner(self)

        self.acceleration = [0, 0.1]
        self.friction = [0.01, 0.01]
        self.max_vel = [10, 10]
        self.angle = 0

    def update_vel(self, dt):#called from hitsop_states
        self.velocity[1] += dt * (self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)
        self.angle = self._get_trajectory_angle()
        self.game_objects.particles.emit('tiny_trail', self.hitbox.center, dir=self.dir,vx=self.velocity[0],vy=self.velocity[1])

    def _get_trajectory_angle(self):
        return math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def pool(game_objects):
        Arrow.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/arrow/', game_objects)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        self.kill()

    def collision_interactables(self,interactable):#collusion interactables
        interactable.seed_collision(self)
        damage_applied, modified_effect = interactable.take_hit(self.create_effect())
        if damage_applied:
            self.velocity = [0,0]
            self.kill()

    def collision_enemy(self,collision_enemy):
        self.kill()

    def handle_platform_collision(self, collision):
        if collision.axis == 'x':
            hit_direction = [1, 0] if collision.side == 'right' else [-1, 0]
        else:
            hit_direction = [0, -1] if collision.side == 'bottom' else [0, 1]

        self._collide_with_platform(hit_direction, collision.collider)

    def _collide_with_platform(self, dir, block):
        self.velocity = [0,0]
        self.seed_spawner.spawn_seed(block, dir)
        self.kill()
