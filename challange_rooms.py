import random
import Entities

class Challange_rooms():
    def __init__(self, game_state, portal):
        self.game_state = game_state
        self.game_objects = game_state.game.game_objects
        self.portal = portal

    def update(self):
        pass

    def render(self):
        pass

    def handle_events(self, input):
        pass 

    def exit_state(self):
        self.portal.currentstate.handle_input('shrink')
        self.game_state.exit_state()        

class Room_0(Challange_rooms):
    def __init__(self, game_state, portal):
        super().__init__(game_state, portal)
        self.number = 1
        for number in range(0,self.number):
            pos = [600 +  random.randint(-100, 100),300 +  random.randint(-100, 100)]
            enemy = Entities.Cultist_rogue(pos, self.game_objects, self)
            self.game_objects.enemies.add(enemy)

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.number -= 1
        if self.number == 0:#all enemies eleminated
            self.exit_state()#if there was a gate, we can open it    
