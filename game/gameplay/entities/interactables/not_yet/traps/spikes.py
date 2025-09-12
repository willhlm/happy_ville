import pygame 
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Spikes(Interactables):#traps
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/traps/spikes/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.rect[2],16)
        self.dmg = 1

