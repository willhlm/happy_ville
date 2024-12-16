import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self, newstate):
        self.entity.death_state = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self, input):
        pass

    def die(self):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def die(self):#"normal" gameplay states calls this
        self.entity.currentstate.enter_state('Death_pre')#overrite any state and go to deat
        self.entity.die()

    def handle_input(self, input):
        if input == 'cultist_encounter':
            self.enter_state('Cultist_encounter')

class Cultist_encounter(Basic_states):#if dying in cultist encounter
    def __init__(self, entity):
        super().__init__(entity)

    def die(self):
        self.entity.game_objects.player.reset_movement()
        self.entity.game_objects.load_map(self.entity.game_objects.game.state_stack[-1], 'dark_forest_1','1')        
        self.enter_state('Idle')#go back to normal

    def handle_input(self, input):
        if input == 'idle':
            self.enter_state('Idle')