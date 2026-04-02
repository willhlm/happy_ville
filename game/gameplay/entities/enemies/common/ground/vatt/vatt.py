import pygame, random 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from engine import constants as C
from gameplay.entities.enemies.common.shared.state_machine import StateManager

from .states import Skip
from .deciders import CheckEdgeSkipDecider

from .config import ENEMY_CONFIG as VATT_CONFIG

VATT_STATES = {
    'skip': Skip,
}

VATT_DECIDERS = {
    'check_edge_skip': CheckEdgeSkipDecider,
}

class Vatt(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.config = VATT_CONFIG['vatt']
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/vatt/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,30)

        self.health = self.config['health']
        self.flags['aggro'] = False

        self.currentstate = StateManager(self, custom_states = VATT_STATES, custom_deciders = VATT_DECIDERS)        
        
        self.shader_state.add_shader('aura', colour = [1, 1, 1], size = 0.8, fall_off = 2, noise_intensity = 3)
        self.time = 0

    def update_render(self, dt):
        super().update_render(dt)
        self.release_particles(dt)

    def release_particles(self, dt):
        self.time += dt 
        if self.time > 30:
            rect = self.hitbox
            position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(rect[3]*0.1,rect[3]*0.5)]
            self.game_objects.particles.emit("spirit_wisp", pos=position, n=2, colour=C.spirit_colour, scale = 5)            
            self.time = 0
