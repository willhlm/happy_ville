import pygame
from gameplay.entities.platforms.texture.base_texture import BaseTexture
from engine.system import animation
from engine.utils import read_files
from . import states_gate

class Gate_1(BaseTexture):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.init()

        self.ID_key = kwarg.get("ID", None)                
        erect = self.game_objects.world_state.load_bool(self.game_objects.map.level_name, "gate", self.ID_key, initial=kwarg.get("erect", False))
        state = "erect" if erect else "down"

        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.animation = animation.Animation(self)
        self.currentstate = {"erect": states_gate.Erect, "down": states_gate.Down}[state](self)
    
        self.game_objects.signals.subscribe(self.ID_key, self.lever_hit)# Lever emits on this channel; gate listens and toggles itself

    def init(self):
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/platforms/gates/gate_1/", self.game_objects)

    def lever_hit(self):
        self.game_objects.world_state.toggle_bool(self.game_objects.map.level_name, "gate", self.ID_key)
        self.currentstate.handle_input("transform")