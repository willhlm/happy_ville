import pygame
from engine import constants as C

class Platform(pygame.sprite.Sprite):
    def __init__(self, pos, size = (16,16), run_particle = 'dust'):
        super().__init__()
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.true_pos = list(self.rect.topleft)
        self.hitbox = self.rect.copy()
        #self.run_particles = {'dust':entities.Dust_running_particles,'water':entities.Water_running_particles,'grass':entities.Grass_running_particles}[run_particle]

    def update_render(self, dt):
        pass

    def update(self, dt):
        pass

    def collide_x(self, entity):
        pass

    def collide_y(self, entity):
        pass

    def draw(self, target):#conly certain platforms will require draw
        pass

    def take_dmg(self, projectile):#called from projectile
        pass

    def release_texture(self):#called when .kill() and empty group
        pass

    def kill(self):
        self.release_texture()#before killing, need to release the textures (but not the onces who has a pool)
        super().kill()

    def jumped(self):#called from player states jump_main
        return C.air_timer
