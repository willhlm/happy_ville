import math, sys, random

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class AI():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]
    
    def enter_AI(self, newAI, **kwarg):        
        self.entity.AI = getattr(sys.modules[__name__], newAI.capitalize())(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys
    
    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx, self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance
    
    def deactivate(self):
        self.enter_AI('idle') 

    def handle_input(self, input):#input is hurt when taking dmg
        pass

class Idle(AI):#do nothing
    def __init__(self, entity):
        super().__init__(entity)   

    def activate(self):
        self.enter_AI('Chase')  

class Wait(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.time = kwarg.get('duration',50)
        self.next_AI = kwarg.get('next_AI','Chase')

    def update(self):   
        self.time -= self.entity.game_objects.game.dt  
        if self.time < 0:
            self.enter_AI(self.next_AI)

class Chase(AI):            
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.chase_direction = 0    
        self.timer = self.entity.game_objects.timer_manager.start_timer(200, self.out_of_range, 'reindeer_range')       

    def update(self):   
        super().update()#get player distance   
        self.chase_direction = sign(self.player_distance[0])        
        self.check_sight()
        self.entity.chase(self.chase_direction)

    def look_target(self):
        self.entity.dir[0] = self.chase_direction

    def check_sight(self):               
        if self.player_distance[0] > 0 and self.entity.dir[0] == -1 or self.player_distance[0] < 0 and self.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.enter_AI('wait', duration = 20)  
            #turn around          
            #wait

        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close             
            if self.entity.flags['attack_able']:
                self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
                self.enter_AI('attack')

        elif abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away                 
            pass
        elif abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:#player within aggro range                           
            self.timer.reset()

    def out_of_range(self):
        self.enter_AI('charge')

class Attack(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.currentstate.handle_input('attack')
        self.next_AI = kwarg.get('next_AI', 'Chase')
        self.entity.flags['attack_able'] = False
        
    def handle_input(self,input):#called from states, depending on if the player was close when it wanted to explode or not
        if input == 'finish_attack':
            self.enter_AI('Wait', duration = 30, next_AI = self.next_AI)          

class Charge(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.currentstate.handle_input('charge')
        self.next_AI = kwarg.get('next_AI', 'Chase')

    def handle_input(self,input):#called from states, depending on if the player was close when it wanted to explode or not
        if input == 'finish_attack':
            self.enter_AI('Wait', duration = 80, next_AI = self.next_AI)    