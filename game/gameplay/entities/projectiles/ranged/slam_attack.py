import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files
from gameplay.entities.shared.components import hit_effects

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
        self.base_effect = hit_effects.create_projectile_effect(damage = self.dmg, hit_type = 'stone', knockback = [25, 0], hitstop = 10, attacker = self)

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

    def clash_particles(self, center, number_particles):
        pass
