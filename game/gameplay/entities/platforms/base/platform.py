import pygame
from gameplay.entities.shared.components.hit.hit_component import HitComponent
from gameplay.entities.platforms.components.surface_collision import SurfaceCollisionComponent

class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, size=(16, 16), run_particle = 'dust'):
        super().__init__()
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.hitbox = self.rect.copy()
        self.true_pos = list(self.rect.topleft)
        self.material = 'stone'
        self.crushes_entities = True
        self.hit_component = HitComponent(self)
        self.hit_component.damage_manager.add_modifier('block_damage')#always block
        self.surface_collision = SurfaceCollisionComponent(self)

    def update_hitbox(self):        
        self.hitbox.topleft = self.rect.topleft# If you use custom hitboxes, override this.

    def update_rect_from_true(self):
        self.rect.left = round(self.true_pos[0])
        self.rect.top  = round(self.true_pos[1])
        self.update_hitbox()

    def update(self, dt):
        pass

    def get_support_motion(self, entity):
        return None

    def get_floor_samples(self, entity):
        return self.surface_collision.get_floor_samples(entity)

    def get_ceiling_samples(self, entity):
        return self.surface_collision.get_ceiling_samples(entity)

    def get_wall_samples(self, entity):
        return self.surface_collision.get_wall_samples(entity)

    def accepts_floor_contact(self, entity, old_hitbox, current_hitbox, target_y, max_step_up):
        return self.surface_collision.accepts_floor_contact(entity, old_hitbox, current_hitbox, target_y, max_step_up)

    def accepts_ceiling_contact(self, entity, old_hitbox, current_hitbox, target_y, max_step_down):
        return self.surface_collision.accepts_ceiling_contact(entity, old_hitbox, current_hitbox, target_y, max_step_down)

    def on_platform_collision(self, entity, side, axis, collision_kind='block'):
        return self.surface_collision.on_platform_collision(entity, side, axis, collision_kind)

    def should_crush_entity(self, entity, side=None):
        return self.crushes_entities

    def handle_entity_crush(self, entity, side=None):
        if self.should_crush_entity(entity, side=side):
            entity.on_crush(self)
            return True

        self.on_crush(entity, side=side)
        return False

    def on_crush(self, entity, side=None):
        pass

    def supports_drop_through(self, entity, probe_hitbox):
        return self.surface_collision.supports_drop_through(entity, probe_hitbox)

    def get_contact_metadata(self, entity, side, axis, collision_kind):
        return self.surface_collision.get_contact_metadata(entity, side, axis, collision_kind)

    def draw(self, target):
        pass

    def update_render(self, dt):
        pass

    def take_hit(self, effect):
        effect.attacker_callbacks.pop('hitstop', None)
        effect.attacker_callbacks.pop('sword_jump', None)        
        return self.hit_component.take_hit(effect)

    def take_dmg(self, effect):#called from hit copmentn
        return effect

    def release_texture(self):#called when .kill() and empty group
        pass
