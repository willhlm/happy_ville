from gameplay.entities.base.platform_entity import PlatformEntity
from gameplay.entities.shared.components import hit_effects

class Projectiles(PlatformEntity):#projectiels
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.lifetime = kwarg.get('lifetime', 300)
        self.flags = {'invincibility': False, 'charge_blocks': kwarg.get('charge_blocks', False), 'aggro': True}#if they can break special blocks        
        self.dmg = kwarg.get('dmg', 1)
        self.base_effect = hit_effects.HitEffect(damage = self.dmg, attacker = self)            

    def update(self, dt):
        super().update(dt)
        self.lifetime -= dt
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    #collisions
    def collision_platform(self, collision_plat):#collision platform
        collision_plat.take_dmg(self)

    def collision_projectile(self, eprojectile):#fprojecticle proectile collision with eprojecitile: called from collisions
        eprojectile.take_dmg(self.dmg)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        if self.flags['aggro']:      
            collision_enemy.take_hit(self.base_effect)

    def collision_interactables(self,interactable):#collusion interactables
        interactable.take_dmg(self)#some will call clash_particles but other will not. So sending self to interactables

    def collision_interactables_fg(self,interactable):#collusion interactables
        pass

    def reflect(self, dir, pos, clamp_value = 10):#projectile collision when purple infinity stone is equipped: pos, dir are aila sword
        dy = max(-clamp_value, min(clamp_value, self.rect.centery - pos[1]))
        dx = max(-clamp_value, min(clamp_value, self.rect.centerx - pos[0]))

        if dir[1] != 0:#up or down
            self.velocity[0] = dx * 0.2
            self.velocity[1] = -10 * dir[1]
        else:#right or left
            self.velocity[0] = 10 * dir[0]
            self.velocity[1] = dy * 0.2

    def take_hit(self, effect):
        pass

    #pltform, ramp collisions.
    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        pass

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        pass

    def right_collision(self, block, type = 'Wall'):
        self.collision_platform(block)

    def left_collision(self, block, type = 'Wall'):
        self.collision_platform(block)

    def down_collision(self, block):
        self.collision_platform(block)

    def top_collision(self, block):
        self.collision_platform(block)

    def limit_y(self):#limits the velocity on ground, onewayup. But not on ramps: it makes a smooth drop
        pass

    def release_texture(self):#i guess all projectiles will have a pool?
        pass

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False