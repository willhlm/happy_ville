import math, sys, random

class AI():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_AI(self, newAI, **kwarg):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def deactivate(self):
        self.enter_AI('Idle') 

    def handle_input(self, input):#input is hurt when taking dmg
        pass

class Idle(AI):#do nothing
    def __init__(self, entity):
        super().__init__(entity)   

class Patrol(AI):#patrol in a circle aorund the original position
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.calculate_postion()  

    def update(self):
        super().update()                        
        self.entity.patrol(self.target_position)
        self.check_position()
        self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_AI('Wait', time = 10, next_AI = 'Chase')

    def check_position(self):
        if abs(self.target_position[0]-self.entity.rect.centerx) < 10 and abs(self.target_position[1]-self.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            self.calculate_postion()
        elif self.entity.collision_types['left'] or self.entity.collision_types['right'] or self.entity.collision_types['bottom'] or self.entity.collision_types['top']:
            self.calculate_postion()

    def calculate_postion(self):
        angle = random.randint(0,180)
        amp = 60
        amp = random.randint(amp-20, amp+20)
        amp = min(amp,80)#cap the amp
        offset = [-20-10*self.entity.dir[0],20-10*self.entity.dir[0]]
        angle = random.randint(angle+offset[0],angle+offset[1])

        self.target_position = [amp*math.cos(math.pi*angle/180) + self.entity.original_pos[0], amp*math.sin(math.pi*angle/180) + self.entity.original_pos[1]]
        self.look_target()

    def look_target(self):
        if self.entity.rect.centerx - self.target_position[0] > 0:
            self.entity.dir[0] = -1
        else:
            self.entity.dir[0] = 1

    def handle_input(self, input):#input is hurt when taking dmg
        if input == 'Hurt':
            self.enter_AI('Chase')

class Wait(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.time = kwarg.get('time',50)
        self.next_AI = kwarg.get('next_AI','Patrol')

    def update(self):   
        self.time -= self.entity.game_objects.game.dt  
        if self.time < 0:
            self.enter_AI(self.next_AI)

    def handle_input(self, input):#input is hurt when taking dmg
        if input == 'Hurt':
            self.enter_AI('Chase')

class Chase(AI):            
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.giveup = kwarg.get('giveup', 300) 
        self.time = self.giveup   

    def update(self):   
        super().update()    
        self.look_target()
        self.entity.chase(self.player_distance)
        self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away     
            self.time -= self.entity.game_objects.game.dt  
            if self.time < 0:
                self.enter_AI('Wait',next_AI = 'Patrol', time = 20)    
        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close 
            self.enter_AI('Attack')
        else:#player close, reset timer
            self.time = self.giveup
 
    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Attack(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.currentstate.handle_input('attack')

    def handle_input(self,input):#called from states, depending on if the player was close when it wanted to explode or not
        if input == 'De_explode':
            self.enter_AI('Wait', next_AI = 'Chase', time = 30)