import sys
import constants as C

class Player_modifier():
    def __init__(self, entity):
        self.entity = entity
        self.entity.friction[1] = C.friction_player[1]

    def enter_state(self, newstate, **kwarg):
        self.entity.player_modifier = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def take_dmg(self, dmg):
        pass

    def falling(self):
        return C.friction_player[1]

    def bubble_jump(self):#called from bubble platform
        return 0.8

    def up_stream(self):#called from up stream collisions
        return 1

    def sword(self):#called from sword in states_player
        pass

class Tjasolmais_embrace(Player_modifier):#enters this state when using the shield
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.shield = kwarg['shield']
        #self.entity.friction[1] = 0.4

    def take_dmg(self, dmg):
        self.shield.take_dmg(dmg)

    def bubble_jump(self):
        return 2

    def up_stream(self):
        return 2

    def falling(self):
        return 0.2

    def sword(self):
        self.shield.kill()
