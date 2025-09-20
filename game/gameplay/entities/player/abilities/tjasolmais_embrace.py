from gameplay.entities.player.base.ability import Ability
from engine.utils import read_files
from gameplay.entities.projectiles import Shield

class TjasolmaisEmbrace(Ability):#makes the shield, water god
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/tjasolmais_embrace/',entity.game_objects)
        self.description = ['shield','hits one additional target','one additional damage','imba']
        self.shield = None#-> higher level can reflect projectiles? or maybe hurt enemy?

    def shield_expire(self):#called when the shield is destroyed
        self.entity.movement_manager.remove_modifier('Tjasolmais_embrace')
        self.entity.damage_manager.remove_modifier('Tjasolmais_embrace')
        self.shield = None

    def sword(self):#called when aila swings the sword
        if self.shield: self.shield.kill()

    def initiate(self):#called when using the abilty
        if self.shield: self.shield.kill()    #kill the old one
        self.shield = Shield(self.entity)
        self.entity.movement_manager.add_modifier('Tjasolmais_embrace', entity = self.entity)
        self.entity.damage_manager.add_modifier('Tjasolmais_embrace', entity = self.entity)

        self.entity.projectiles.add(self.shield)

