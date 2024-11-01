import math, sys, random

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class AI():#parent AI
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
        self.append_child(Idle(self))

    def activate(self):#assumes that the last in list is idle         
        self.children.pop()

class Idle():
    def __init__(self, parent, **kwarg):
        self.parent = parent

    def update(self):
        pass    

    def handle_input(self, input):#input is hurt when taking dmg
        pass

    def go_aggro(self):
        self.parent.children = self.parent.children[:1]#remove all except patrol
        self.parent.append_child(Aggro(self.parent, give_up = 300))

class Patrol(Idle):
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.calculate_postion()

    def calculate_postion(self):
        angle = random.randint(0,180)
        amp = 60
        amp = random.randint(amp-20, amp+20)
        amp = min(amp,80)#cap the amp
        offset = [-20-10*self.parent.entity.dir[0],20-10*self.parent.entity.dir[0]]
        angle = random.randint(angle+offset[0],angle+offset[1])

        self.target_position = [amp*math.cos(math.pi*angle/180) + self.parent.entity.original_pos[0], amp*math.sin(math.pi*angle/180) + self.parent.entity.original_pos[1]]
        self.look_target()

    def look_target(self):
        if self.parent.entity.rect.centerx - self.target_position[0] > 0:
            self.parent.entity.dir[0] = -1
        else:
            self.parent.entity.dir[0] = 1

    def check_position(self):
        if abs(self.target_position[0]-self.parent.entity.rect.centerx) < 10 and abs(self.target_position[1]-self.parent.entity.rect.centery) < 10:#5*self.init_time > 2*math.pi
            self.calculate_postion()
        elif self.parent.entity.collision_types['left'] or self.parent.entity.collision_types['right'] or self.parent.entity.collision_types['bottom'] or self.parent.entity.collision_types['top']:
            self.calculate_postion()

    def update(self):
        self.check_position()            
        if self.check_sight(): return#do not continue if this happens
        self.parent.entity.patrol(self.target_position)

    def check_sight(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.aggro_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.aggro_distance[1]:
            self.parent.append_child(Aggro(self.parent, give_up = 300))
            return True
        return False

    def handle_input(self, input):
        if input == 'Hurt':
            self.go_aggro()     

class Wait(Idle):#the entity should just stay and do nothing for a while
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.duration = kwarg.get('duration',200)

    def update(self):
        self.duration -= self.parent.entity.game_objects.game.dt
        if self.duration < 0:
            self.parent.pop_child() 

    def handle_input(self, input):
        if input == 'Hurt':
            self.go_aggro()

class Turn_around(Idle):#when the player jumps over, should be a delays before the entity turns around
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        
    def update(self):
        self.parent.entity.dir[0] = -self.parent.entity.dir[0]                    
        self.parent.pop_child()         

    def handle_input(self, input):
        if input == 'Hurt':
            self.go_aggro()

class Aggro(Idle):
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.timer_jobs = {'attack_cooldown': Timer(self, duration = kwarg.get('attack_cooldown', 100), function = self.on_attack_cooldown), 'give_up': Timer(self, duration = kwarg.get('give_up', 300), function = self.on_giveup)}#if player is out of sight for more than duration, go to peace, else, remain
        self.timers = []
        self.attack_able = True
        self.chase_direction = [0,0]

    def update(self):
        self.update_timers()

        self.check_sight()    
        self.look_player()#make the direction along the player. If this happens, do not continue in update            
        self.flee()
        self.attack()#are we withtin attack distance? If this happens, do not continue in update
        
        self.parent.entity.chase(self.chase_direction) 

    def check_sight(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.aggro_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.aggro_distance[1]:#if wihtin sight, stay in chase
            self.timer_jobs['give_up'].restore()
        else:#out of sight
            self.timer_jobs['give_up'].activate()   
            self.chase_direction = [sign(self.parent.player_distance[0]), sign(self.parent.player_distance[1])]     

    def look_player(self):#look at the player
        if self.parent.player_distance[0] > 0 and self.parent.entity.dir[0] == -1 or self.parent.player_distance[0] < 0 and self.parent.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.parent.append_child(Wait(self.parent, duration = 20))
            self.parent.append_child(Turn_around(self.parent))    
            self.parent.append_child(Wait(self.parent, duration = 20))  

    def attack(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.attack_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.attack_distance[1]:
            if self.attack_able:
                self.parent.append_child(Wait(self.parent, duration = 20))        
                self.parent.append_child(Attack(self.parent))
                self.timer_jobs['attack_cooldown'].activate() 
                self.attack_able = False

    def flee(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.flee_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.flee_distance[1]:#player close 
            self.chase_direction = [-sign(self.parent.player_distance[0]), -sign(self.parent.player_distance[1])]          

    def update_timers(self):
        for timer in self.timers:
            timer.update()        

    def on_giveup(self):#when giveup timer runs out
        self.parent.pop_child()#stop chasing

    def on_attack_cooldown(self):#when attack cooldown timer runs out
        self.attack_able = True              

class Attack(Idle):
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.parent.entity.currentstate.handle_input('attack')

    def handle_input(self,input):
        if input == 'finish_attack':
            self.parent.pop_child()

class Timer():
    def __init__(self, AI, duration, function):
        self.AI = AI
        self.duration = duration
        self.function = function

    def restore(self):
        self.lifetime = self.duration

    def activate(self):#add timer to the entity timer list
        if self in self.AI.timers: return#do not append if the timer is already inside
        self.restore()
        self.AI.timers.append(self)

    def deactivate(self):
        self.AI.timers.remove(self)
        self.function()

    def update(self):
        self.lifetime -= self.AI.parent.entity.game_objects.game.dt
        if self.lifetime < 0:
            self.deactivate()
