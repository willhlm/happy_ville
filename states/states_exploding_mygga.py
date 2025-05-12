import sys, math, random

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class Enemy_states():
    def __init__(self,entity):
        self.entity = entity
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def deactivate(self):
        self.enter_state('Idle') 

    def handle_input(self, input):#input is hurt when taking dmg
        pass

    def increase_phase(self):
        pass

class Idle(Enemy_states):#do nothing
    def __init__(self, entity):
        super().__init__(entity)   
        self.entity.animation.play('idle')

class Patrol(Enemy_states):#patrol in a circle aorund the original position
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('walk')
        self.calculate_postion()  
        self.time = 0

    def update(self):
        super().update()                        
        self.time += 0.02 * self.entity.game_objects.game.dt
        self.entity.patrol(self.target_position)
        self.entity.sway(self.time)#sway up and down
        self.check_position()
        self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_state('Wait', time = 10, next_state = 'Chase')

    def check_position(self):
        if abs(self.target_position[0]-self.entity.rect.centerx) < 10 and abs(self.target_position[1]-self.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            self.enter_state('Wait', time = 15)
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

        self.target_position = [amp*math.cos(math.pi * angle/180) + self.entity.original_pos[0], amp*math.sin(math.pi*angle/180) + self.entity.original_pos[1]]
        self.look_target()

    def look_target(self):
        if self.entity.rect.centerx - self.target_position[0] > 0:
            self.entity.dir[0] = -1
        else:
            self.entity.dir[0] = 1

class Wait(Enemy_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.time = kwarg.get('time',50)
        self.next_state = kwarg.get('next_state','Patrol')
        self.entity.animation.play('idle')

    def update(self):   
        self.time -= self.entity.game_objects.game.dt  
        if self.time < 0:
            self.enter_state(self.next_state)

class Chase(Enemy_states): #chase player           
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.giveup = kwarg.get('giveup', 300) 
        self.time = self.giveup   
        self.init_time = 0
        self.entity.animation.play('walk')

    def update(self):   
        super().update()    
        self.init_time += 0.02 * self.entity.game_objects.game.dt
        self.look_target()
        self.entity.chase(self.player_distance)
        self.entity.sway(self.init_time)
        self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away     
            self.time -= self.entity.game_objects.game.dt  
            if self.time < 0:
                self.enter_state('Wait',next_state = 'Patrol', time = 20)    
        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close 
            self.enter_state('Attack_pre')
        else:#player close, reset timer
            self.time = self.giveup
 
    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Attack_pre(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.animation.play('pre_explode')

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        if abs(self.player_distance[0]) > self.entity.attack_distance[0] or abs(self.player_distance[1]) > self.entity.attack_distance[1] :#player close 
            self.enter_state('De_explode')
        else:
            self.enter_state('Death')

class De_explode(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)   
        self.entity.animation.play('de_explode')     

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.enter_state('Wait', next_state = 'Chase')

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.animation.play('death')
        self.entity.killed()

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.dead()
