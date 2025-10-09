import pygame
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects
from . import states_droplet_source
from gameplay.entities.projectiles import FallingRock

class FallingRockSource(LayeredObjects):
    animations = {}    
    def __init__(self, pos, game_objects, parallax,layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name,live_blur)
        self.init_sprites('assets/sprites/entities/interactables/sources/falling_rock/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.currentstate = states_droplet_source.Idle(self)

    def drop(self):#called from states
        obj = FallingRock(self.rect.bottomleft, self.game_objects)
        self.game_objects.eprojectiles.add(obj)
