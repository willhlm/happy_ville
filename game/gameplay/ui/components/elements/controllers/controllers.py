import pygame
from engine.system import animation
from . import states_buttons
from engine.utils import read_files

class Controllers():
    def __init__(self, pos, game_objects, button, type):
        self.game_objects = game_objects#animation need it
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/controller/' + type + '/',game_objects)
        name = button + '_idle'
        self.image = self.sprites[name][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)        

        self.animation = animation.Animation(self)
        self.currentstate =  getattr(states_buttons, button.capitalize() + '_idle')(self)
        self.animation.play(name)        
        
    def reset_timer(self):#animation neeed it
        pass

    def update(self, dt):
        self.animation.update(dt)

    def render(self, target):  
        self.game_objects.game.display.render(self.image, target, position=self.rect.topleft)

