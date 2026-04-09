from .base_ability import Ability
from engine.utils import read_files
from gameplay.entities.projectiles import Arrow

class JuksakkasBlessing(Ability):#arrow -> fetillity god
    id = 'bow'
    name = 'Bow'
    state_name = 'bow'
    spirit_cost = 1
    selectable = True

    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/juksakkas_blessing/', entity.game_objects)
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

    def initiate(self, dir, time):#called when relasing the button
        self.entity.game_objects.projectiles.add_friendly(Arrow(pos = self.entity.hitbox.topleft, game_objects = self.entity.game_objects, dir = dir, lifetime = 50, time = time))#add attack to group
