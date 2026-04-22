from gameplay.entities.projectiles.base.projectile_base import ProjectileBase
from gameplay.entities.shared.components.body.melee_body import MeleeBody
from gameplay.entities.shared.components.hit import hit_effects

class Melee(ProjectileBase):
    def __init__(self, entity, **kwarg):
        super().__init__([0,0], entity.game_objects, **kwarg)
        self.entity = entity#needs entity for making the hitbox follow the player in update hitbox
        self.dir = kwarg.get('dir', entity.dir.copy())
        self.body = MeleeBody(self)

    def update(self, dt):
        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.body.update_hitbox()
        self.lifetime -= scaled_dt
        self.destroy()

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        effect = self.create_effect()
        collision_enemy.take_hit(effect)     

    def create_effect(self):
        #pm_one = sign(collision_enemy.hitbox.center[0]-self.entity.hitbox.center[0])
        return hit_effects.HitEffect(self.game_objects, damage = self.dmg, attacker = self)                     
