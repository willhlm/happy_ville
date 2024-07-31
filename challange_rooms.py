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

    def failiure(self):#called when fail the chalange
        pass

    def handle_input(self, input, **kwarg):
        if input == 'death':#normal death
            self.game_objects.player.death()   
            self.failiure()  
            self.exit_state()                   

    def exit_state(self):
        self.game_state.exit_state()     

class Ball_room(Challange_rooms):#the room with ball in light forest cave
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state)
        pos = kwarg.get('position', [0,0]) 
        self.number = 5#number of balls
        self.time = 600        
        self.spawn_balls(pos)
        self.get_gates()
                                
        self.timer = Entities.Timer_display(self, self.time)
        self.game_objects.cosmetics_no_clear.add(self.timer)          
    
    def spawn_balls(self, pos):
        for i in range(0, self.number):
            new_ball = Entities.Bouncy_balls(pos, self.game_objects, gameplay_state = self, lifetime = self.time)         
            self.game_objects.eprojectiles.add(new_ball)   

    def time_out(self):#when timer runs out
        self.failiure()

    def get_gates(self):#trap aila
        self.gates = {}
        for gate in self.game_objects.map.references['gate']:
            if gate.ID_key == 'ball_room1':#these strings are specified in tiled
                gate.currentstate.handle_input('Transform')       
                self.gates['1'] = gate
            elif gate.ID_key == 'ball_room':#these strings are specified in tiled
                self.gates['2'] = gate#this one is already erect
       
    def failiure(self):
        self.timer.kill()
        self.gates['1'].currentstate.handle_input('Transform')   

    def complete(self):
        self.timer.kill()
        self.game_objects.world_state.state[self.game_objects.map.level_name]['challenge_monument'][type(self).__name__.lower()] = True#completed            
        for key in self.gates.keys():#open the gates
            self.gates[key].currentstate.handle_input('Transform')     
        self.exit_state()                   

    def increase_kill(self):#called wgeb ball is destroyed
        self.number -= 1
        if self.number <= 0:
            self.complete()        

class Portal_rooms(Challange_rooms):#challanges with portals
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state)
        pos = kwarg.get('position', [0,0])        
        self.portal = Entities.Portal([pos[0] + 200, pos[1] - 50], self.game_objects, state = self)        
        self.game_objects.special_shaders.add(self.portal)        
        
    def initiate_room(self):#portal calls it after growing
        pass

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

    def initiate_room(self):
        self.put_gate()
        self.number = 1
        for number in range(0,self.number):
            pos = [600 +  random.randint(-100, 100), 300 +  random.randint(-100, 100)]
            enemy = Entities.Cultist_rogue(pos, self.game_objects, self)
            self.game_objects.enemies.add(enemy)

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.number -= 1
        if self.number == 0:#all enemies eleminated        
            self.complete()#if there was a gate, we can open it    
    
    def complete(self):
        self.game_objects.world_state.state[self.game_objects.map.level_name]['challenge_monument'][type(self).__name__.lower()] = True#completed                
        self.exit_state()

    def exit_state(self):
        super().exit_state()
        for gate in self.gates:
            gate.kill()        
