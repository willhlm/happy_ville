from gameplay.entities.player.abilities import horagalles_rage, tjasolmais_embrace, juksakkas_blessing, bieggs_breath, beaivis_time, dash, wall_glide, double_jump

class AbilityManager():#Player movement abilities, handles them. Contains also spirit abilities
    def __init__(self,entity):
        self.entity = entity
        self.spirit_abilities = {'Thunder': horagalles_rage.HoragallesRage(entity),'Shield': tjasolmais_embrace.TjasolmaisEmbrace(entity),'Bow': juksakkas_blessing.JuksakkasBlessing(entity),'Wind': bieggs_breath.BieggsBreath(entity),'Slow_motion': beaivis_time.BeaivisTime(entity)}#abilities aila has
        self.equip = 'Thunder'#spirit ability pointer
        self.movement_dict = {'Dash':dash.Dash(entity),'Wall_glide':wall_glide.WallGlide(entity),'Double_jump':double_jump.DoubleJump(entity)}#abilities the player has
        self.movement_abilities = list(self.movement_dict.values())#make it a list


