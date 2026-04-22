import random, math
from engine.utils import read_files
from engine.system import animation
from gameplay.entities.shared.states import states_basic
from gameplay.entities.platforms.base.dynamic_platform import DynamicPlatform

class Bubble(DynamicPlatform):#dynamic one: #shoudl be added to platforms and dynamic_platforms groups
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.crushes_entities = False
        self.sprites = Bubble.sprites
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.old_hitbox = self.hitbox.copy()
        self.cos_amp_scaler = prop.get('cos_amp_scaler', 1) #hould be between 0 and 1

        self.max_down_vel = 0.5
        self.max_up_vel = -1
        self.accel = 3
        self.collided_y = False
        self.collided_right = False
        self.collided_left = False

        lifetime = prop.get('lifetime', 100000)
        self.game_objects.timer_manager.start_timer(lifetime, self.deactivate)

        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#s
        self.sign = 1
        self.sin_time = random.randint(0, 180)

    def jumped(self):#called from player states jump_main
        self.deactivate()
        context = self.game_objects.player.movement_manager.resolve()
        return context.air_timer

    def update_vel(self, dt):
        x_col_vel = 2
        self.sign = 1
        if self.collided_y:
            self.sign = -1
            #self.accel = 40
            self.velocity[1] -= self.sign * self.accel * 10 * dt*0.01
            self.velocity[1] = min(self.velocity[1], self.max_down_vel)
            self.velocity[0] = 0
        elif self.collided_right:
            self.velocity[1] -= self.sign * self.accel * dt*0.01
            self.velocity[1] = max(self.velocity[1], self.max_up_vel)
            self.velocity[0] = x_col_vel
        elif self.collided_left:
            self.velocity[1] -= self.sign * self.accel * dt*0.01
            self.velocity[1] = max(self.velocity[1], self.max_up_vel)
            self.velocity[0] = -1 * x_col_vel
        else:
            self.velocity[1] -= self.sign * self.accel * dt*0.01
            self.velocity[1] = max(self.velocity[1], self.max_up_vel)
            self.sin_time += dt
            sin_vel = math.sin(self.sin_time/30)/40
            self.velocity[0] += sin_vel * self.cos_amp_scaler
            self.velocity[0] += dt*(0 - 0.06*self.velocity[0])
        #self.velocity[0] += dt*(0 - 0.1*self.velocity[0])

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        if axis == 'x':
            if side == 'right':
                self.collided_right = True
            elif side == 'left':
                self.collided_left = True
            return

        if axis == 'y':
            if side == 'bottom':
                self.collided_y = True
            elif side == 'top':
                self.deactivate()

    def release_texture(self):
        pass

    def pool(game_objects):#all things that should be saved in object pool
        Bubble.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/bubble/', game_objects)

    def take_dmg(self, projectile):
        self.deactivate()

    def deactivate(self):#called when first timer runs out
        self.kill()

    def on_crush(self, entity, side=None):
        self.deactivate()

    def update(self, dt):
        super().update(dt)
        self.collided_y = False
        self.collided_right = False
        self.collided_left = False
        self.collisions()

    def collisions(self):#check collisions with static and dynamic platforms
        for platform in self.game_objects.physics.platform_spatial_index.query_rect(self.hitbox):
            if platform is self: continue#skip self
            self.platform_collision(platform)

        for interactable in self.game_objects.interactables_fg:#check for upstream collisions
            if type(interactable).__name__ == 'Up_stream':
                if self.hitbox.colliderect(interactable.hitbox):
                    dir = interactable.dir.copy()
                    self.velocity[0] += dir[0] * 0.1
                    self.velocity[1] += dir[1] * 0.1

    def platform_collision(self, platform):# Determine the direction of collision based on velocity and relative positions
        if self.velocity[1] > 0:  # Moving down
            if self.hitbox.bottom > platform.hitbox.top and self.hitbox.top < platform.hitbox.bottom:# Collision from the top of the platform
            # self.rect.bottom = platform.hitbox.top  # Resolve collision
                self.deactivate()  # Call your method or logic for deactivating
        elif self.velocity[1] < 0:  # Moving up
            if self.hitbox.top < platform.hitbox.bottom and self.hitbox.bottom > platform.hitbox.top:# Collision from the bottom of the platform
                #self.rect.top = platform.hitbox.bottom  # Resolve collision
                self.deactivate()

        if self.velocity[0] > 0:  # Moving right
            if self.hitbox.right > platform.hitbox.left and self.hitbox.left < platform.hitbox.right:# Collision from the left side of the platform
                #self.rect.right = platform.hitbox.left  # Resolve collision
                pass
        elif self.velocity[0] < 0:  # Moving left
            if self.hitbox.left < platform.hitbox.right and self.hitbox.right > platform.hitbox.left:# Collision from the right side of the platform
                pass
                #self.rect.left = platform.hitbox.right  # Resolve collision
