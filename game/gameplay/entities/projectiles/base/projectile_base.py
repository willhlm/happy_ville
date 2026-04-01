from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.components.body.entity_body import EntityBody
from gameplay.entities.shared.components.hit.hitstop_component import HitstopComponent
from gameplay.entities.shared.components.hit import hit_effects


class ProjectileBase(AnimatedEntity):
    uses_platform_physics = False

    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.body = EntityBody(self)
        self.hitstop = HitstopComponent()
        self.velocity = [0, 0]
        self.lifetime = kwarg.get('lifetime', 300)
        self.flags = {'invincibility': False, 'charge_blocks': kwarg.get('charge_blocks', False), 'aggro': True}
        self.dmg = kwarg.get('dmg', 1)

    def update(self, dt):
        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        super().update(scaled_dt)

        if not self.uses_platform_physics:
            self.body.update_true_pos_x(scaled_dt)
            self.body.update_true_pos_y(scaled_dt)

        self.lifetime -= scaled_dt
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def collision_platform(self, collision_plat):
        effect = self.create_effect()
        damage_applied, modified_effect = collision_plat.take_hit(effect)

    def collision_projectile(self, eprojectile):
        effect = self.create_effect()
        damage_applied, modified_effect = eprojectile.take_hit(effect)

    def collision_enemy(self, collision_enemy):
        effect = self.create_effect()
        damage_applied, modified_effect = collision_enemy.take_hit(effect)

    def collision_interactables(self, inetractable):
        effect = self.create_effect()
        damage_applied, modified_effect = inetractable.take_hit(effect)

    def collision_interactables_fg(self, interactable):
        pass

    def reflect(self, dir, pos, clamp_value=10):
        dy = max(-clamp_value, min(clamp_value, self.rect.centery - pos[1]))
        dx = max(-clamp_value, min(clamp_value, self.rect.centerx - pos[0]))

        if dir[1] != 0:
            self.velocity[0] = dx * 0.2
            self.velocity[1] = -10 * dir[1]
        else:
            self.velocity[0] = 10 * dir[0]
            self.velocity[1] = dy * 0.2

    def take_hit(self, effect):
        pass

    def create_effect(self):
        return hit_effects.HitEffect(self.game_objects, damage=self.dmg, attacker=self)

    def release_texture(self):
        pass

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

