import pygame
from gameplay.entities.platforms.texture.base_texture import BaseTexture
from engine.system import animation
from engine.utils import read_files
from . import states_bridge

class Bridge(BaseTexture):#bridge twoards forest path
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/bridge/', game_objects)

        if game_objects.world_state.events.get('reindeer', False):#if reindeer has been deafeated
            state = 'erect'
        else:
            state = 'down'

        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_bridge.Erect, 'down': states_bridge.Down}[state](self)
