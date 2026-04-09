from .base_ability import Ability
from engine.utils import read_files
from gameplay.entities.projectiles import Wind

class BieggsBreath(Ability):#force push
    id = 'wind'
    name = 'Wind'
    state_name = 'wind'
    spirit_cost = 1
    selectable = True

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
        self.entity.game_objects.projectiles.add_friendly(spawn)

    def level_up(self):
        super().level_up()
        if self.level == 2:
            self.health = 2
        return self
