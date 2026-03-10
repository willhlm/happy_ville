from gameplay.entities.player.abilities import horagalles_rage, tjasolmais_embrace, juksakkas_blessing, bieggs_breath, beaivis_time

class AbilityManager():#Player movement abilities, handles them. Contains also spirit abilities
    def __init__(self,entity):
        self.entity = entity
        self.spirit_abilities = {'Thunder': horagalles_rage.HoragallesRage(entity),'Shield': tjasolmais_embrace.TjasolmaisEmbrace(entity),'Bow': juksakkas_blessing.JuksakkasBlessing(entity),'Wind': bieggs_breath.BieggsBreath(entity),'Slow_motion': beaivis_time.BeaivisTime(entity)}#abilities aila has
        self.equip = 'Thunder'#spirit ability pointer: used for selecting abilties in wheel

    def update(self, dt):
        for ability in self.spirit_abilities.values():
            ability.update(dt)