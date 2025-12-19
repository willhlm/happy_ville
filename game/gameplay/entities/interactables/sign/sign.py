import pygame 
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.interactables.sign.symbols import Symbols


class Sign(Interactables):
    def __init__(self,pos,game_objects,directions):
        super().__init__(pos,game_objects)
        self.directions = directions
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/sign/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=self.rect.copy()
        self.symbols = Symbols(self)

    def collision(self, entity):#player collision
        self.currentstate.handle_input('Outline')

    def noncollision(self, entity):#when player doesn't collide
        self.symbols.finish()
        self.currentstate.handle_input('Idle')

    def interact(self):#when player press t/y
        if self.symbols in self.game_objects.cosmetics:
            self.symbols.finish()
        else:
            self.symbols.init()
            self.game_objects.cosmetics.add(self.symbols)