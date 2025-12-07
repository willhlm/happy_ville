from .base_ability import Ability
from engine.utils import read_files
from gameplay.entities.projectiles import Wind

class BieggsBreath(Ability):#force push
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities//bieggs_breath/',entity.game_objects)
        self.health = 1
        self.description = ['wind','hard wind']

    def initiate(self):#called when using the ability
        if self.entity.dir[1] == 0:#left or right
            dir = self.entity.dir.copy()
        else:#up or down
            dir = [0,-self.entity.dir[1]]

        spawn = Wind(self.entity.hitbox.midtop, self.entity.game_objects, dir = dir, dmg = 0)
        self.entity.game_objects.fprojectiles.add(spawn)

    def upgrade_ability(self):#called from upgrade menu
        self.level += 1
        if self.level == 2:
            self.health = 2

