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
        self.check_position()
        self.check_sight()
        self.entity.patrol(self.target_position)

    def check_position(self):
        if abs(self.target_position[0]-self.entity.rect.centerx) < 10 and abs(self.target_position[1]-self.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            self.calculate_postion()
        elif self.entity.collision_types['left'] or self.entity.collision_types['right'] or self.entity.collision_types['bottom'] or self.entity.collision_types['top']:
            self.calculate_postion()

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_AI('Wait', time = 10, next_AI = 'Chase')

    def calculate_postion(self):
        angle = random.randint(0,180)
        amp = 60
        amp = random.randint(amp-20, amp+20)
        amp = min(amp,80)#cap the amp
        offset = [-20-10*self.entity.dir[0],20-10*self.entity.dir[0]]
        angle = random.randint(angle+offset[0],angle+offset[1])
        self.target_position = [amp*math.cos(math.pi*angle/180) + self.entity.original_pos[0], amp*math.sin(math.pi*angle/180) + self.entity.original_pos[1]]
        self.entity.dir[0] = -sign(self.entity.rect.centerx - self.target_position[0])
        
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

class Chase(AI):#keep some distance and keep attacking            
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.give_up_duration = kwarg.get('give_up', 300)
        self.chase_direction = [0, 0]   

    def update(self):   
        super().update()   
        self.chase_direction = [sign(self.player_distance[0]), sign(self.player_distance[1])]        
        self.look_target()
        self.check_sight()
        self.entity.chase(self.chase_direction)

    def look_target(self):
        self.entity.dir[0] = sign(self.player_distance[0])

    def check_sight(self):        
        if abs(self.player_distance[0]) < self.entity.flee_distance[0] and abs(self.player_distance[1]) < self.entity.flee_distance[1]:#player close close 
            self.enter_AI('Flee')
            self.entity.game_objects.timer_manager.remove_ID_timer('giveup')#remove the giveup timer if exist, before changing state
        
        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close             
            if self.entity.flags['attack_able']:
                self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
                self.enter_AI('Attack')
                self.entity.game_objects.timer_manager.remove_ID_timer('giveup')#remove the giveup timer if exist, before changing state

        elif abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away     
            self.entity.game_objects.timer_manager.start_timer(self.give_up_duration, self.on_giveup, ID = 'giveup')#adds a timer to timer_manager and sets self.invincible to false after a while

    def on_giveup(self):#when giveup timer runs out
        self.enter_AI('Wait', next_AI = 'Patrol', time = 20)  

class Flee(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)            

    def update(self):   
        super().update()  
        self.chase_direction = [-sign(self.player_distance[0]), -sign(self.player_distance[1])]                
        self.look_target()
        self.check_sight()
        self.attack()#attack while fleeing        
        self.entity.chase(self.chase_direction)
    
    def look_target(self):
        self.entity.dir[0] = sign(self.player_distance[0]) 

    def check_sight(self):              
        if abs(self.player_distance[0]) > self.entity.attack_distance[0] or abs(self.player_distance[1]) > self.entity.attack_distance[1]:#player close 
            self.enter_AI('Chase')

    def attack(self):
        if self.entity.flags['attack_able']:
            self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            self.enter_AI('Attack', next_AI = 'Flee')#attack while fleeing  

class Attack(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.currentstate.handle_input('attack')
        self.next_AI = kwarg.get('next_AI', 'Chase')
        self.entity.flags['attack_able'] = False
        
    def handle_input(self,input):#called from states, depending on if the player was close when it wanted to explode or not
        if input == 'finish_attack':
            self.enter_AI('Wait', time = 30, next_AI = self.next_AI)          