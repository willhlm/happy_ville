import pygame, random
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files

class BouncyBalls(Projectiles):#for ball challange room
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = BouncyBalls.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.dmg = 1
        self.light = game_objects.lights.add_light(self)
        self.velocity = [random.uniform(-10,10),random.uniform(-10,-4)]

    def pool(game_objects):
        BouncyBalls.sprites = read_files.load_sprites_dict('assets/sprites/attack/projectile_1/',game_objects)

    def release_texture(self):
        pass

    def kill(self):#when lifeitme runs out or hit by aila sword
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    def take_dmg(self, dmg):#when hit by aila sword without purple stone
        self.velocity = [0,0]
        self.dmg = 0
        self.currentstate.handle_input('Death')
        self.game_objects.signals.emit('ball_killed')

    #platform collisions
    def right_collision(self, block, type = 'Wall'):
        self.hitbox.right = block.hitbox.left
        self.collision_types['right'] = True
        self.currentstate.handle_input(type)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self, block, type = 'Wall'):
        self.hitbox.left = block.hitbox.right
        self.collision_types['left'] = True
        self.currentstate.handle_input(type)
        self.velocity[0] = -self.velocity[0]

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = -self.velocity[1]

    def down_collision(self, block):
        self.hitbox.bottom = block.hitbox.top
        self.collision_types['bottom'] = True
        self.velocity[1] *= -1
