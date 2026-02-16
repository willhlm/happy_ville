import pygame

class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, size=(16, 16), run_particle = 'dust'):
        super().__init__()
        self.true_pos = [float(pos[0]), float(pos[1])]
        self.rect = pygame.Rect(round(self.true_pos[0]), round(self.true_pos[1]), size[0], size[1])
        self.hitbox = self.rect.copy()

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

    def take_dmg(self, effect):
        pass        

    def release_texture(self):#called when .kill() and empty group
        pass        