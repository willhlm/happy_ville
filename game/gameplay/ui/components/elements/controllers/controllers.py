import pygame
from engine.system import animation
from engine.controller import PROMPT_TYPES
from . import states_buttons
from engine.utils import read_files

class Controllers():
    def __init__(self, pos, game_objects, button):
        self.game_objects = game_objects#animation need it
        self.button = button
        self.sprite_sets = {
            prompt_type: read_files.load_sprites_dict(
                'assets/sprites/ui/elements/controller/' + prompt_type + '/', game_objects
            )
            for prompt_type in PROMPT_TYPES
        }
        self.prompt_type = None
        self._set_prompt_type(game_objects.controller.prompt_type)
        name = button + '_idle'
        self.image = self.sprite_sets[self.prompt_type][name][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)        

        self.animation = animation.Animation(self)
        self.currentstate =  getattr(states_buttons, button.capitalize() + '_idle')(self)
        self.animation.play(name)        
        
    def reset_timer(self):#animation neeed it
        pass

    def update(self, dt):
        self._sync_prompt_type()
        self.animation.update(dt)

    def _sync_prompt_type(self):
        if self.prompt_type == self.game_objects.controller.prompt_type:
            return
        self._set_prompt_type(self.game_objects.controller.prompt_type)
        self.animation.play(self.button + '_idle')

    def _set_prompt_type(self, prompt_type):
        self.sprites = self.sprite_sets[prompt_type]
        self.prompt_type = prompt_type
        self.image = self.sprites[self.button + '_idle'][0]

    def render(self, target):  
        self._sync_prompt_type()
        self.game_objects.game.display.render(self.image, target, position=self.rect.topleft)
