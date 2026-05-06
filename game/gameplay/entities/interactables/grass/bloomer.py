import pygame
import random
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Bloomer(Interactables):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/grass/hlifblom/bloomer/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)        
        self.hitbox.midbottom = self.rect.midbottom
        
        self.bloomed = False
        self.bloom_stimulus = None
        self.bloom_light = None

        self.shader_state.add_shader('sway', offset=random.uniform(0.0, 10.0), speed=0.012, min_strength=0.006, max_strength=0.028, strength_scale=10.0, interval=4.2, detail=1.1, height_offset=0.08, upsidedown=0.0)

    def take_dmg(self, effect):
        self.release_particles(3)
        if self.bloomed:
            return effect

        self.bloomed = True
        self.currentstate.handle_input('bloom')
        self.bloom_stimulus = self.game_objects.stimuli.register_source(self, channel='light', radius=300, strength=1.6, falloff=0.0015, tags={'flower'})
        self.bloom_light = self.game_objects.lights.add_light(self, radius=300, colour=[255 / 255, 255 / 255, 255 / 255, 1.0])

        return effect

    def release_particles(self, number_particles = 12):#should release particles when hurt and death
        self.game_objects.particles.emit('circle_wave', self.hitbox.center, n = 12, distance = 30, colour = [180,220,255,255])    

    def on_collision(self, entity):#one time collision
        pass
        
    def on_noncollision(self, entity):#one time none collision
        pass

    def on_kill_cleanup(self):
        if self.bloom_stimulus is not None:
            self.game_objects.stimuli.unregister_source(self.bloom_stimulus)
            self.bloom_stimulus = None

        if self.bloom_light is not None:
            self.game_objects.lights.remove_light(self.bloom_light)
            self.bloom_light = None
