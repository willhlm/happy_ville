import sys, random
from states_entity import Entity_States

class Basic_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update_state(self):
        pass

    def handle_input(self,input):
        if input == 'Hurt':
            self.enter_state('Hurt')

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0]:
            self.enter_state('Birth')

class Birth(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.loot.add(self.entity.item(self.entity.rect.center,self.entity.game_objects,'omamori'))

    def increase_phase(self):
        self.enter_state('Idle2')

class Idle2(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.state_name = 'idle'

class Hurt(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
