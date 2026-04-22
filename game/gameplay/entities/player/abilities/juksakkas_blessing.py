from .base_ability import Ability
from engine.utils import read_files
from gameplay.entities.projectiles import Arrow

class JuksakkasBlessing(Ability):#arrow -> fetillity god
    id = 'bow'
    name = 'Bow'
    state_name = 'bow'
    spirit_cost = 1
    selectable = True
    max_level = 2

    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/juksakkas_blessing/', entity.game_objects)
        self.description = [
            'Fire a spirit arrow with charge-based power.',
            'Charged arrows can spawn different spirit effects.',
        ]

    def initiate(self, dir, time):#called when relasing the button
        self.entity.game_objects.projectiles.add_friendly(Arrow(pos = self.entity.hitbox.topleft, game_objects = self.entity.game_objects, dir = dir, lifetime = 50, time = time))#add attack to group
