from gameplay.entities.player.base.ability import Ability
from engine.utils import read_files
from gameplay.entities.projectiles import Arrow

class JuksakkasBlessing(Ability):#arrow -> fetillity god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/attack/UI/juksakkas_blessing/', entity.game_objects)
        self.level = 1#upgrade pointer
        self.description = ['shoot arrow','charge arrows','charge for insta kill','imba']

    def initiate(self, dir, time):#called when relasing the button
        self.entity.projectiles.add(Arrow(pos = self.entity.hitbox.topleft, game_objects = self.entity.game_objects, dir = dir, lifetime = 50, time = time))#add attack to group