from .base_ability import Ability
from engine.utils import read_files

class HoragallesRage(Ability):#desolate dive:thunder god:
    id = 'thunder'
    name = 'Thunder'
    state_name = 'thunder'
    spirit_cost = 1
    selectable = True

    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/horagalles_rage/',entity.game_objects)
        self.description = ['thunder','hits one additional target','one additional damage','imba']

    def initiate(self, enemy_rect):
        thunder = Thunder(enemy_rect, self.entity.game_objects, lifetime =  1000)
        thunder.rect.midbottom = enemy_rect.midbottom
        thunder.hitbox = thunder.rect.copy()
        self.entity.game_objects.projectiles.add_friendly(thunder)#add attack to group
