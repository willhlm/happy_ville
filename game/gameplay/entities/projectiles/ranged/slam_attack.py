import pygame, random
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files
from gameplay.entities.shared.components import hit_effects
from gameplay.entities.visuals.particles import particles

class SlamAttack(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)
        self.sprites = SlamAttack.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.currentstate.enter_state('Death')
        self.animation.play('idle')
        self.dir = kwarg.get('dir', [1, 0])
        self.base_effect = hit_effects.create_projectile_effect(damage = self.dmg, hit_type = 'stone', knockback = [25, 0], hitstop = 10, projectile = self)

    def pool(game_objects):
        SlamAttack.sprites = read_files.load_sprites_dict('assets/sprites/entities/projectiles/slam/', game_objects, flip_x = True)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        effect = self.base_effect.copy()
        effect.meta['attacker_dir'] = self.dir#save the direction
        collision_enemy.take_hit(effect)                        

    def collision_platform(self, collision_plat):#collision platform
        pass

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        eprojectile.take_dmg(self.dmg)

    def apply_hitstop(self, lifetime, call_back):
        pass

    def clash_particles(self, pos, number_particles=12):
        angle = random.randint(-180, 180)#the erection anglex
        color = [255, 255, 255, 255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos, self.game_objects, distance = 0, lifetime = 10, vel = {'linear':[5,7]}, dir = angle, scale = 0.8, fade_scale = 7, colour = color)
            self.game_objects.cosmetics.add(obj1)
