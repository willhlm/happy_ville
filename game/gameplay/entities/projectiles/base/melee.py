import random
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils.functions import sign
from gameplay.entities.visuals.particles import particles

class Melee(Projectiles):
    def __init__(self, entity, **kwarg):
        super().__init__([0,0], entity.game_objects, **kwarg)
        self.entity = entity#needs entity for making the hitbox follow the player in update hitbox
        self.dir = kwarg.get('dir', entity.dir.copy())
        self.direction_mapping = {(0, 0): ('center', 'center'), (1, 1): ('midbottom', 'midtop'),(-1, 1): ('midbottom', 'midtop'), (1, -1): ('midtop', 'midbottom'),(-1, -1): ('midtop', 'midbottom'),(1, 0): ('midleft', 'midright'),(-1, 0): ('midright', 'midleft')}        

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        if self.flags['aggro']:
            pm_one = sign(collision_enemy.hitbox.center[0]-self.entity.hitbox.center[0])
            effect = self.base_effect.copy()
            effect.meta['attacker_dir'] = [pm_one, 0]
            collision_enemy.take_hit(effect)     

    def update_hitbox(self):#called from update hirbox in plaform entity
        rounded_dir = (sign(self.dir[0]), sign(self.dir[1]))#analogue controls may have none integer values
        hitbox_attr, entity_attr = self.direction_mapping[rounded_dir]
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes

    def reflect(self, dir, pos):#called from sword collision_projectile, purple initinty stone
        return
        self.entity.countered()
        self.kill()

    def update_rect_y(self):
        pass

    def update_rect_x(self):
        pass

    def clash_particles(self, pos, number_particles=12):
        angle = random.randint(-180, 180)#the erection anglex
        color = [255, 255, 255, 255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, distance = 0, lifetime = 10, vel = {'linear':[5,7]}, dir = angle, scale = 0.8, fade_scale = 7, colour = color)
            self.entity.game_objects.cosmetics.add(obj1)
