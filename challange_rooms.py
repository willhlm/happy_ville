import random
import Entities
import platforms

class Challange_rooms():
    def __init__(self, game_state):
        self.game_state = game_state
        self.game_objects = game_state.game.game_objects

    def update(self):
        pass

    def render(self):
        pass

    def handle_events(self, input):
        pass 

    def exit_state(self):
        self.game_state.exit_state()        

class Ball_room(Challange_rooms):#the room with ball in light forest cave
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state)
        pass

class Portal_rooms(Challange_rooms):#challanges with portals
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state)
        self.portal = kwarg['portal']     
        self.put_gate() 

    def put_gate(self):        
        pos = [self.portal.rect.topleft, self.portal.rect.topright]
        self.gates = []
        for num in range(0,2):
            self.gates.append(Entities.Bubble_gate(pos[num],self.game_objects,[100,340]))
            self.game_objects.interactables.add(self.gates[-1])                       

    def exit_state(self):
        self.portal.currentstate.handle_input('shrink')
        super().exit_state()  

class Room_0(Portal_rooms):
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg)
        self.number = 1
        for number in range(0,self.number):
            pos = [600 +  random.randint(-100, 100), 300 +  random.randint(-100, 100)]
            enemy = Entities.Cultist_rogue(pos, self.game_objects, self)
            self.game_objects.enemies.add(enemy)

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.number -= 1
        if self.number == 0:#all enemies eleminated
            self.exit_state()#if there was a gate, we can open it    
