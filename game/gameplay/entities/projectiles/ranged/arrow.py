import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files
from gameplay.entities.projectiles import seeds
from gameplay.visuals.particles import particles

class Arrow(Projectiles):#should it be called seed?
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
        self.seed_spawner = seeds.SeedSpawner(self)

        self.once = False

        self.acceleration = [0, 0.1]
        self.friction = [0.01, 0.01]
        self.max_vel = [10, 10]

    def update_vel(self, dt):#called from hitsop_states
        self.velocity[1] += dt * (self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)
        self.angle = self._get_trajectory_angle()
        self.emit_particles(lifetime = 50, dir = self.dir, vel = {'linear': [self.velocity[0] * 0.1, self.velocity[1] * 0.1]}, scale = 0.5, fade_scale = 5)

    def emit_particles(self, type = 'Circle', **kwarg):
        obj1 = getattr(particles, type)(self.hitbox.center, self.game_objects, **kwarg)
        self.game_objects.cosmetics.add(obj1)

    def _get_trajectory_angle(self):
        return math.degrees(math.atan2(self.velocity[1], self.velocity[0]))

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0)#shader render

    def pool(game_objects):
        Arrow.sprites = read_files.load_sprites_dict('assets/sprites/attack/arrow/', game_objects)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        self.kill()

    def collision_interactables(self,interactable):#collusion interactables
        pass

    def collision_interactables_fg(self, interactable):#collusion interactables_fg: e.g. twoDliquid
        if self.once: return
        self.once = True
        interactable.seed_collision(self)
        self.velocity = [0,0]
        self.kill()

    def collision_enemy(self,collision_enemy):
        self.kill()

    def right_collision(self, block, type = 'Wall'):
        self.collision_platform([1, 0], block)

    def left_collision(self, block, type = 'Wall'):
        self.collision_platform([-1, 0], block)

    def down_collision(self, block):
        self.collision_platform([0, -1], block)

    def top_collision(self, block):
        self.collision_platform([0, 1], block)

    def collision_platform(self, dir, block):
        self.velocity = [0,0]
        if self.once: return
        self.once = True
        self.seed_spawner.spawn_seed(block, dir)
        self.kill()
