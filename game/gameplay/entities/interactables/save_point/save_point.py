import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from . import states_savepoint
from gameplay.ui.components import LogoLoading

class SavePoint(Interactables):#save point
    def __init__(self, pos, game_objects, map):
        super().__init__(pos, game_objects)
        self.sprites=read_files.load_sprites_dict('assets/sprites/entities/interactables/savepoint/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]
        self.currentstate = states_savepoint.Idle(self)

    def interact(self):#when player press t/y
        self.game_objects.player.currentstate.enter_state('crouch')
        self.game_objects.player.backpack.map.save_savepoint(map =  self.map, point = self.init_cord)
        self.currentstate.handle_input('active')
        self.game_objects.cosmetics.add(LogoLoading(self.game_objects))

