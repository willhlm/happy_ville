import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class Rooms(AnimatedEntity):#the rroms in map
    def __init__(self, pos, game_objects, number):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/map/rooms/nordveden/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)        
        self.room_number = number

#inventory
