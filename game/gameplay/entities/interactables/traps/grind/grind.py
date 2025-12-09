import pygame, math
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_grind
from gameplay.entities.shared.components import hit_effects

class Grind(Interactables):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/traps/grind/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate = states_grind.Active(self)#

        self.frequency = int(kwarg.get('frequency', -1))#infinte -> idle - active
        direction = kwarg.get('direction', '0,0')#standing still
        string_list = direction.split(',')
        self.direction = [int(num) for num in string_list]
        self.distance = int(kwarg.get('distance', 1))/16
        self.speed = float(kwarg.get('speed', 1))

        self.velocity = [0, 0]
        self.time = 0

        self.base_effect = hit_effects.create_contact_effect(damage = 1, hit_type = 'metal', hitstop = 10, attacker = self)

    def update_vel(self):
        self.velocity[0] = self.direction[0] * self.distance * math.cos(self.speed * self.time)
        self.velocity[1] = self.direction[1] * self.distance * math.sin(self.speed * self.time + math.pi*0.5) 

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.currentstate.update(dt)
        self.update_vel()
        self.update_pos(dt)

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0] * dt, self.true_pos[1] + self.velocity[1] * dt]
        self.rect.topleft = self.true_pos
        self.hitbox.center = self.rect.center

    def group_distance(self):
        pass

    def player_collision(self, player):#player collision
        effect = self.base_effect.copy()
        effect.meta['attacker_dir'] = [0,0]#save the direction
        #effect.particles['dir'] = self.dir        

        damage_applied, modified_effect = player.take_hit(effect)                        

    def take_dmg(self, projectile):#when player hits with e.g. sword
        if hasattr(projectile, 'sword_jump'):#if it has the attribute
            projectile.sword_jump()

