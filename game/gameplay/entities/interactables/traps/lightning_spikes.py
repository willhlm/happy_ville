import pygame 
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_traps

class LightningSpikes(Interactables):#traps
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/traps/lightning_spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 26, 16)
        self.size = [64,64]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Once')

