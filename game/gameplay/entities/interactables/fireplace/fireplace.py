import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_fireplace

class Fireplace(Interactables):
    def __init__(self, pos, game_objects, on = False):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/interactables/fireplace/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/fireplace/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom
        
        self.currentstate = states_fireplace.Idle(self)
        self.light_sources = []#save light references to turn be able to removr them
        if on:
            self.interact()        

        self.hit_component.set_invinsibility(True)

    def interact(self):  # when player press t/y
        self.currentstate.handle_input('Interact')  # goes to interacted after transform

    def turn_on(self):#called from sttes
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [255/255,175/255,100/255,255/255],flicker=True,radius = 100))
        self.light_sources.append(self.game_objects.lights.add_light(self, flicker = True, radius = 50))
        self.light_sources.append(self.game_objects.lights.add_light(self, colour = [255/255,175/255,100/255,255/255],radius = 100))

        self.spatial_emitter_id = self.game_objects.sound.register_spatial_point(self.sounds['idle'][0], get_point=lambda: self.hitbox.center, base_volume=1, loops=-1, min_dist=48, max_dist=500)

    def turn_off(self):#called from sttes
        for light in self.light_sources:
            self.game_objects.lights.remove_light(light)
        self.light_sources = []   
        self.game_objects.sound.unregister_emitter(self.spatial_emitter_id)
       