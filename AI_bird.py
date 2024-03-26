import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_AI(self,newAI):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        if abs(self.player_distance[0])<self.entity.aggro_distance[0]:
            self.enter_AI('Fly')

    def deactivate(self):
        pass 

class Idle(AI):
    def __init__(self,entity):
        super().__init__(entity) 
        self.entity.currentstate.enter_state('Idle') 
        self.duration = random.randint(10,100)

    def update(self):
        super().update()
        self.duration -= self.entity.game_objects.game.dt
        if self.duration < 0:
            self.next_state()

    def next_state(self):
        rand = random.randint(1,4)
        if rand==1:#go back being idle
            self.duration = random.randint(10,100)
        elif rand==2:
            self.enter_AI('Eat')
        elif rand==3:
            self.enter_AI('Walk')                   
        elif rand==4:
            self.enter_AI('Turn')            

class Walk(AI):
    def __init__(self,entity):
        super().__init__(entity) 
        self.entity.currentstate.enter_state('Walk') 
        self.duration = random.randint(10,100)

    def update(self):
        super().update()
        self.duration -= self.entity.game_objects.game.dt
        if self.duration < 0:
            self.next_state()
    
    def next_state(self):
        rand = random.randint(1,2)
        if rand==1:
            self.enter_AI('Idle')
        elif rand==2:
            self.enter_AI('Turn')

class Turn(AI):
    def __init__(self,entity):
        super().__init__(entity)  
        self.entity.currentstate.enter_state('Idle')         
        self.duration = 20

    def update(self):
        super().update()
        self.duration -= self.entity.game_objects.game.dt
        if self.duration < 0:
            self.entity.dir[0] = -self.entity.dir[0]             
            self.enter_AI('Idle')     
                    
class Fly(AI):
    def __init__(self,entity):
        super().__init__(entity) 
        self.entity.currentstate.enter_state('Fly') 

    def update(self):
        pass

class Eat(AI):
    def __init__(self,entity):
        super().__init__(entity) 
        self.entity.currentstate.enter_state('Eat')   

    def finish_animation(self):#called when anmation is finished from states
        self.enter_AI('Idle')         