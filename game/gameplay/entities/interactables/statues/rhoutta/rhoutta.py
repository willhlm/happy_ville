import pygame, random
from engine import constants as C
from engine.utils import read_files
from engine.utils.functions import track_distance
from gameplay.entities.interactables.base.interactables import Interactables

class RhouttaStatue(Interactables):#interact with it to get air dash
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/statues/rhoutta/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.interacted = False
        if self.interacted: 
            self.animation.play('idle')
        else:
            self.animation.play('old')

    def update(self, dt):
        super().update(dt)
        amplitude = track_distance(self.game_objects.player.hitbox.center, self.hitbox.center)
        self.emit_particles()

    def emit_particles(self):
        rect = self.hitbox
        position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(rect[3]*0.1,rect[3]*0.5)]
        self.game_objects.particles.emit('spirit_wisp', position, colour =[0,0,0,255])

    def draw(self, target):
        super().draw(target)
        
    def interact(self):#when player press t/y
        if self.interacted: return        
        self.interacted = True
        self.game_objects.signals.emit('open')
        #self.game_objects.map.load_map(self.game_objects.game.state_manager.state_stack[-1],'rhoutta_encounter_1','1')
