from gameplay.entities.base.animated_entity import AnimatedEntity
import random
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.hit import hit_effects
from gameplay.entities.projectiles.base.projectile_clash_component import ProjectileClashComponent

class ProjectileBase(AnimatedEntity):
    uses_platform_collider = False
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.body = EntityBody(self)
        self.hitstop = HitstopComponent()
        self.velocity = [0, 0]
        self.lifetime = kwarg.get('lifetime', 300)
        self.flags = {'invincibility': False, 'charge_blocks': kwarg.get('charge_blocks', False), 'aggro': True}
        self.dmg = kwarg.get('dmg', 1)
        self.team = kwarg.get('team', None)
        self.projectile_clash = ProjectileClashComponent(self)

    def update(self, dt):
        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.projectile_clash.update(scaled_dt)
        super().update(scaled_dt)#animation and currentstate update

        self.lifetime -= scaled_dt
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def collision_platform(self, collision_plat):
        effect = self.create_effect()
        damage_applied, modified_effect = collision_plat.take_hit(effect)

    def collision_enemy(self, collision_enemy):
        effect = self.create_effect()
        damage_applied, modified_effect = collision_enemy.take_hit(effect)

    def collision_interactables(self, inetractable):
        effect = self.create_effect()
        damage_applied, modified_effect = inetractable.take_hit(effect)

    def collision_projectile(self, eprojectile):
        self.projectile_clash.handle_collision(eprojectile)        

    def modify_projectile_clash_result(self, other, result):
        return result

    def on_projectile_clash_ignored(self, other):
        pass

    def on_projectile_clash_won(self, other):
        pass

    def on_projectile_clash_lost(self, other):
        self.kill()

    def on_projectile_reflected(self, other, direction, position, team=None, clamp_value=10):
        pass

    def create_projectile_clash_effect(self, other, result):
        center_x = (self.hitbox.centerx + other.hitbox.centerx) * 0.5
        center_y = (self.hitbox.centery + other.hitbox.centery) * 0.5
        return hit_effects.create_projectile_clash_effect(
            self.game_objects,
            attacker=self,
            projectile=self,
            hit_type='sword',
            attacker_particles={
                'preset': 'sword_clash',
                'n': 5,
                'args': {
                    'angle': random.randint(-180, 180),
                    'colour': [255, 255, 255, 255],
                },
            },
            meta={'clash_pos': [center_x, center_y]},
        )

    def create_effect(self):
        return hit_effects.HitEffect(self.game_objects, damage=self.dmg, attacker=self)

    def release_texture(self):
        pass