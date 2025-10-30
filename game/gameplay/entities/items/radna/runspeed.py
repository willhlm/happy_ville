import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class Runspeed(Radna):#increase the runs speed
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)