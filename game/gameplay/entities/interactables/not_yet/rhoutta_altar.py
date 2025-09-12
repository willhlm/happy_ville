import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Rhoutta_altar(Interactables):#altar to trigger the cutscane at the beginning
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/rhoutta_altar/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()

    def player_collision(self, player):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
        self.game_objects.game.state_manager.enter_state(state_name = 'Rhoutta_encounter', category = 'cutscenes')

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

