from .base_ability import Ability
from engine.utils import read_files
from gameplay.entities.effects import SlowmotionField

class BeaivisTime(Ability):#slow motion -> sun god: Beaiviáigi in sami
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/beaivis_time/', entity.game_objects)

    def initiate(self):#called when using the ability from player states
        position = self.entity.hitbox.center
        self.entity.game_objects.cosmetics.add(SlowmotionField(position, self.entity.game_objects))           

