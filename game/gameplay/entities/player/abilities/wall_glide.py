from gameplay.entities.player.base.ability import Ability
from engine.utils import read_files

class WallGlide(Ability):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities//Wall_glide/',entity.game_objects)
        self.image = self.sprites['idle_1'][0]
        self.description = ['wall glide','free wall jumps','donno','donno']

