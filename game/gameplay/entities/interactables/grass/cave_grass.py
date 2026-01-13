import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.visuals.particles import particles

class InteractableCaveGrass(Interactables):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/grass/hlifblom/cave_grass/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)        
        self.hitbox.midbottom = self.rect.midbottom

        self.flags['invincibility'] = False

    def on_collision(self, entity):
        self.currentstate.handle_input('Once',animation_name ='hurt', next_state = 'Idle')
        self.release_particles()

    def take_dmg(self, damage):
        self.currentstate.handle_input('Death')
        self.release_particles(3)
        self.flags['invincibility'] = True                          

    def release_particles(self, number_particles = 12):#should release particles when hurt and death
        for i in range(0, number_particles):
            obj1 = getattr(particles, 'Circle')(self.hitbox.center,self.game_objects, distance=30, lifetime=300, vel = {'wave': [3, 14]}, scale=2, fade_scale = 1.5)
            self.game_objects.cosmetics.add(obj1)        

    def on_noncollision(self, entity):
        self.currentstate.handle_input('Idle')
