import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class ShadowLightLantern(Interactables):#emits a shadow light upon interaction. Shadow light inetracts with dark forest enemy and platofrm
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/shadow_light_lantern/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.light_sources = []
        if kwarg.get('on', False):
            self.make_light()

    def interact(self):#when player press t/y
        if not self.light_sources:
            self.make_light()
        else:
            for light in self.light_sources:
                self.game_objects.lights.remove_light(light)
            self.light_sources = []

    def make_light(self):
        self.light_sources.append(self.game_objects.lights.add_light(self, shadow_interact = False, colour = [100/255,175/255,255/255,255/255],flicker=True,radius = 300))
        self.light_sources.append(self.game_objects.lights.add_light(self, radius = 250, colour = [100/255,175/255,255/255,255/255],flicker=True))
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [100/255,175/255,255/255,255/255],radius = 200))