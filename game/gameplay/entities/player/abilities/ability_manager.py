from gameplay.entities.player.abilities import horagalles_rage, tjasolmais_embrace, juksakkas_blessing, bieggs_breath, beaivis_time, dash, wall_glide, double_jump

class AbilityManager():#Player movement abilities, handles them. Contains also spirit abilities
    def __init__(self,entity):
        self.entity = entity
        self.spirit_abilities = {'Thunder': horagalles_rage.HoragallesRage(entity),'Shield': tjasolmais_embrace.TjasolmaisEmbrace(entity),'Bow': juksakkas_blessing.JuksakkasBlessing(entity),'Wind': bieggs_breath.BieggsBreath(entity),'Slow_motion': beaivis_time.BeaivisTime(entity)}#abilities aila has
        self.equip = 'Thunder'#spirit ability pointer
        self.movement_dict = {'Dash':dash.Dash(entity),'Wall_glide':wall_glide.WallGlide(entity),'Double_jump':double_jump.DoubleJump(entity)}#abilities the player has
        self.movement_abilities = list(self.movement_dict.values())#make it a list
        self.number = 3#number of movement abilities one can have equiped, the equiped one will be appended to self.entity.states

    def remove_ability(self):#movement stuff
        abilities = self.movement_abilities[0:self.number]#the abilities currently equiped
        for ability in abilities:#remove ability
            string = ability.__class__.__name__
            self.entity.states.remove(string)

    def add_ability(self):#movement stuff
        abilities = self.movement_abilities[0:self.number]#the abilities to be equiped
        for ability in abilities:#at tthe ones we have equipped
            string = ability.__class__.__name__
            self.entity.states.add(string)

    def increase_number(self):#movement stuff
        self.number += 1
        self.number = min(self.number,3)#limit the number of abilities one can equip at the same time

    def handle_input(self, value):#movement stuff
        if value[0] == 1:#pressed right
            self.remove_ability()
            self.movement_abilities = self.movement_abilities[-1:] + self.movement_abilities[:-1]#rotate the abilityes to the right
            self.entity.game_objects.ui['gameplay'].init_ability()
            self.add_ability()
        elif value[0] == -1:#pressed left
            self.remove_ability()
            self.movement_abilities = self.movement_abilities[1:] + self.movement_abilities[:1]#rotate the abilityes to the left
            self.entity.game_objects.ui['gameplay'].init_ability()
            self.add_ability()
        elif value[1] == 1:#pressed up
            pass
        elif value[1] == -1:#pressed down
            pass

