from .base_ability import Ability
from engine.utils import read_files

class Dash(Ability):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/Dash/',entity.game_objects)
        self.image = self.sprites['idle_1'][0]
        self.description = ['dash','free dash','invinsible dash','dash attack']

