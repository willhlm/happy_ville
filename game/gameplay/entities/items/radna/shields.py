import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class Shields(Radna):#autoamtic shield that negates one damage, if have been outside combat for a while?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)