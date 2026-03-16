from engine.system import animation
from gameplay.entities.shared.states import states_basic

class Ability():#aila abilities
    def __init__(self,entity):
        self.entity = entity
        self.game_objects = entity.game_objects        

        self.level = 1#upgrade pointer

    def level_up(self):
        self.level += 1

    def initiate(self):#called when using the ability
        pass

    def update(self, dt):#called from ability manager
        pass