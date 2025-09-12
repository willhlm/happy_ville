import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Air_dash_statue(Interactables):#interact with it to get air dash
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/statues/air_dash_statue/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

        self.interacted = self.game_objects.player.states.get('Air_dash', False)

        self.shader_state = {False : states_shader.Idle, True: states_shader.Tint}[self.interacted](self, colour = [0,0,0,100])
        self.text = 'dash in air'

    def draw(self, target):
        self.shader_state.draw()
        super().draw(target)

    def interact(self):#when player press t/y
        if self.interacted: return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.game_objects.player.states['Air_dash'] = True#give ability
        self.shader_state.handle_input('tint', colour = [0,0,0,100])
        self.interacted = True

        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.game_objects.player.sprites['air_dash_main'][0], text = self.text, callback = self.on_exit)

    def on_exit(self):#called when eiting the blit_image_text state
        self.game_objects.player.currentstate.handle_input('Pray_post')#needed when picked up Interactable_item