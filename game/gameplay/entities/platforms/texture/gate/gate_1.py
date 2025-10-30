import pygame
from gameplay.entities.platforms.texture.base_texture import BaseTexture
from engine.system import animation
from engine.utils import read_files
from . import states_gate

class Gate_1(BaseTexture):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.init()

        self.ID_key = kwarg.get('ID', 'None')#an ID to match with the gate
        if game_objects.world_state.quests.get(self.ID_key[:self.ID_key.rfind('_')], False):#if quest accodicated with it has been completed
            state = 'down'
        elif game_objects.world_state.events.get(self.ID_key[:self.ID_key.rfind('_')], False):#if the event has been completed
            state = 'down'
        else:
            state = {True: 'erect', False: 'down'}[kwarg.get('erect', False)]#a flag that can be specified in titled
        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)#hitbox is set in state

        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

    def init(self):
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/gates/gate_1/', self.game_objects)
