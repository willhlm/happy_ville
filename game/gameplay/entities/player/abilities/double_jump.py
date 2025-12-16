from .base_ability import Ability
from engine.utils import read_files

class DoubleJump(Ability):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/Double_jump/',entity.game_objects)
        self.image = self.sprites['idle_1'][0]
        self.description = ['doulbe jump','free double jump','donno','donno']