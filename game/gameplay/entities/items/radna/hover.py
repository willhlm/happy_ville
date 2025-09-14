import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class Hover(Radna):#If holding jump button, make a small hover
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)