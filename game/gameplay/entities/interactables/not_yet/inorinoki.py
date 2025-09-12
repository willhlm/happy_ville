import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Inorinoki(Interactables):#the place where you trade soul essence for spirit or heart contrainer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/inorinoki/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

    def interact(self):#when player press t/y
        self.game_objects.game.state_manager.enter_state(state_name = 'Soul_essence', category = 'game_states_facilities')

