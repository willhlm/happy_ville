import pygame
from engine.utils import read_files
from gameplay.entities.items.radna.base_radna import Radna

class Dashpeed(Radna):#decrease the dash cooldown?
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)