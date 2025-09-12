import pygame 
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Grind(Interactables):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/traps/grind/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_grind.Active(self)#

        self.frequency = int(kwarg.get('frequency', -1))#infinte -> idle - active
        direction = kwarg.get('direction', '0,0')#standing still
        string_list = direction.split(',')
        self.direction = [int(num) for num in string_list]
        self.distance = int(kwarg.get('distance', 1))#standing still
        self.speed = float(kwarg.get('speed', 1))

        self.velocity = [0, 0]
        self.time = 0
        self.original_pos = pos

    def update_vel(self):
        self.velocity[0] = self.direction[0] * self.distance * math.cos(self.speed * self.time)
        self.velocity[1] = self.direction[1] * self.distance * math.sin(self.speed * self.time)

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.currentstate.update()
        self.update_vel()
        self.update_pos(dt)

    def update_pos(self, dt):
        self.true_pos = [self.original_pos[0] + self.velocity[0] * dt,self.original_pos[1] + self.velocity[1] * dt]
        self.rect.topleft = self.true_pos
        self.hitbox.center = self.rect.center

    def group_distance(self):
        pass

    def player_collision(self, player):#player collision
        player.take_dmg(dmg = 1)

    def take_dmg(self, projectile):#when player hits with e.g. sword
        if hasattr(projectile, 'sword_jump'):#if it has the attribute
            projectile.sword_jump()

