import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.children = [Patrol(self)]    
        self.player_distance = [0,0]

    def update(self):#the init will run the same frame but its update in the next
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx, self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance
        self.children[-1].update()

    def append_child(self, child):#the init will run the same frame but its update in the next
        self.children.append(child)
    
    def pop_child(self):
        self.children.pop()

    def handle_input(self, input):
        self.children[-1].handle_input(input)

    def deactivate(self):#used for cutscene or when they die
        self.append_child(Idle())

class Idle():
    def __init__(self, **kwarg):
        pass

    def update(self):
        pass    

class Patrol():
    def __init__(self, parent, **kwarg):
        self.parent = parent
        self.time = 0

    def update(self):
        self.time += self.parent.entity.game_objects.game.dt                
        self.check_sight()

    def check_sight(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.attack_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.attack_distance[1]:
            self.parent.append_child(Init_Fade_animation(self.parent))
            self.parent.append_child(Wait(self.parent, duration = 40))            
            self.parent.append_child(Fly(self.parent))
            self.parent.append_child(Wait(self.parent, duration = 40))
            self.parent.append_child(Fly(self.parent))             
        elif abs(self.parent.player_distance[0]) < self.parent.entity.aggro_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.aggro_distance[1]:
            self.parent.append_child(Taunt(self.parent))     
            self.parent.append_child(Init_taunt_animation(self.parent))     

class Init_taunt_animation():
    def __init__(self,parent,**kwarg):
        self.parent = parent

    def update(self):
        self.parent.entity.currentstate.enter_state('Taunt')
        self.parent.pop_child()

class Taunt():
    def __init__(self,parent,**kwarg):
        self.parent = parent

    def update(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.attack_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.attack_distance[1]:
            self.parent.pop_child()
            self.parent.append_child(Init_Fade_animation(self.parent))
            self.parent.append_child(Wait(self.parent,duration = 40))
            self.parent.append_child(Fly(self.parent))
            self.parent.append_child(Wait(self.parent,duration = 40))
            self.parent.append_child(Fly(self.parent))
        elif abs(self.parent.player_distance[0]) > self.parent.entity.aggro_distance[0] or abs(self.parent.player_distance[1]) > self.parent.entity.aggro_distance[1]:#player is far away                        
            self.parent.entity.currentstate.handle_input('idle')
            self.parent.pop_child()            

class Init_Fade_animation():
    def __init__(self,parent,**kwarg):
        self.parent = parent

    def update(self):
        self.parent.entity.currentstate.handle_input('fade')

class Wait():
    def __init__(self,parent,**kwarg):
        self.parent = parent
        self.duration = kwarg.get('duration',100)

    def update(self):
        self.parent.entity.velocity[0] = 0
        self.duration -= self.parent.entity.game_objects.game.dt                
        if self.duration < 0:
            self.parent.pop_child()

class Fly():
    def __init__(self,parent,**kwarg):
        self.parent = parent

    def update(self):
        if self.parent.player_distance[0] > 0:
            self.parent.entity.dir[0] = 1
        else:
            self.parent.entity.dir[0] = -1

        self.parent.entity.velocity[0] += -self.parent.entity.dir[0]*4

    def handle_input(self, input):
        if input == 'landed':
            self.parent.pop_child()