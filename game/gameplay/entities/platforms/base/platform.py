import pygame
from gameplay.entities.shared.components.hit_component import HitComponent

class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, size=(16, 16), run_particle = 'dust'):
        super().__init__()
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.hitbox = self.rect.copy()
        self.true_pos = list(self.rect.topleft)
        self.material = 'stone'
        self.hit_component = HitComponent(self)
        self.hit_component.damage_manager.add_modifier('block_damage')#always block

    def update_hitbox(self):        
        self.hitbox.topleft = self.rect.topleft# If you use custom hitboxes, override this.

    def update_rect_from_true(self):
        self.rect.left = round(self.true_pos[0])
        self.rect.top  = round(self.true_pos[1])
        self.update_hitbox()

    def update(self, dt):
        pass

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