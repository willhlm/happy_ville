import sys, random

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
        self.parent.append_child(Chase(self.parent, give_up = 300))

class Patrol(Idle):
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.time = 0

    def update(self):
        self.time += self.parent.entity.game_objects.game.dt                
        if self.check_sight(): return#do not continue if this happens
        if self.check_ground(): return#do not continue if this happens
        if self.check_wall(): return#do not continue if this happens
        self.parent.entity.patrol([0,0])
        self.exit()

    def check_sight(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.aggro_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.aggro_distance[1]:
            self.parent.append_child(Aggro(self.parent))
            return True
        return False

    def check_wall(self):
        if self.parent.entity.collision_types['left'] or self.parent.entity.collision_types['right']:            
            self.parent.append_child(Wait(self.parent, duration = 200))
            self.parent.append_child(Turn_around(self.parent))    
            self.parent.append_child(Wait(self.parent, duration = 100))
            return True
        return False
            
    def check_ground(self):#this will always trigger when the enemy spawn, if they are spawn in air in tiled
        point = [self.parent.entity.hitbox.midbottom[0] + self.parent.entity.dir[0]*self.parent.entity.hitbox[3],self.parent.entity.hitbox.midbottom[1] + 8]
        collide = self.parent.entity.game_objects.collisions.check_ground(point)
        if not collide:#there is no ground in front
            self.parent.append_child(Wait(self.parent, duration = 100))
            self.parent.append_child(Turn_around(self.parent))    
            self.parent.append_child(Wait(self.parent, duration = 100))
            return True
        return False

    def exit(self):
        if self.time > 200:
            child = random.choice(['Wait','Turn_around'])#choose between turnaround and wait            
            child_node = getattr(sys.modules[__name__], child)(self.parent)#make a class based on the name of the newstate: need to import sys
            self.parent.append_child(child_node)
            self.time = 0  

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
        self.timer_jobs = {'attack_cooldown': Timer(self, duration = kwarg.get('attack_cooldown', 50), function = self.on_attack_cooldown), 'give_up': Timer(self, duration = kwarg.get('give_up', 300), function = self.on_giveup)}#if player is out of sight for more than duration, go to peace, else, remain
        self.timers = []
        self.attack_able = True
        self.dir = self.parent.entity.dir[0]  #chase direction

    def update(self):
        self.check_sight()#if aggro or not
        self.update_timers()

        if self.check_distance(): return #chekc if player too close and if we should hide
        if self.attack(): return#are we withtin attack distance? If this happens, do not continue in update        
        if self.check_ground(): return#do not continue if this happens -> do not chase down a cliff. but still agro so projectiles can be shot (it is set after self.attack)
        self.parent.entity.chase(self.dir) 

    def check_sight(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.aggro_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.aggro_distance[1]:#if wihtin sight, stay in chase
            self.timer_jobs['give_up'].restore()
        else:#out of sight
            self.timer_jobs['give_up'].activate()        

    def check_distance(self):
        #if player too clsoe, it hides
        if abs(self.parent.player_distance[0]) < self.parent.entity.hide_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.hide_distance[1]:
            self.parent.append_child(Hide(self.parent)) 
            return True 
        #go away from player
        elif abs(self.parent.player_distance[0]) < self.parent.entity.fly_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.fly_distance[1]:
            if self.parent.player_distance[0] > 0 and self.dir == 1 or self.parent.player_distance[0] < 0 and self.dir == -1:#player on right and looking at left#player on left and looking right                       
                self.dir *= -1#chase direction
                self.parent.append_child(Wait(self.parent, duration = 20))
                return True
        
        elif abs(self.parent.player_distance[0]) > self.parent.entity.attack_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.attack_distance[1]:
            if self.parent.player_distance[0] > 0 and self.dir == -1 or self.parent.player_distance[0] < 0 and self.dir == 1:#player on right and looking at left#player on left and looking right                       
                self.dir *= -1#chase direction
                self.parent.append_child(Wait(self.parent, duration = 20))
                return True

        #look at player    
        elif self.parent.player_distance[0] > 0 and self.parent.entity.dir[0] == -1 or self.parent.player_distance[0] < 0 and self.parent.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right
            self.parent.append_child(Wait(self.parent, duration = 20))
            self.parent.append_child(Turn_around(self.parent))    
            self.parent.append_child(Wait(self.parent, duration = 20))  
            return True
        return False  
            
    def attack(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.attack_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.attack_distance[1]:
            if self.attack_able:
                self.parent.append_child(Wait(self.parent, duration = 20))        
                self.parent.append_child(Attack(self.parent))
                self.timer_jobs['attack_cooldown'].activate() 
                self.attack_able = False
                return True
        return False

    def update_timers(self):
        for timer in self.timers:
            timer.update()    
            
    def check_ground(self):#this will always trigger when the enemy spawn, if they are spawn in air in tiled
        point = [self.parent.entity.hitbox.midbottom[0] + self.parent.entity.dir[0]*self.parent.entity.hitbox[3],self.parent.entity.hitbox.midbottom[1] + 8]
        collide = self.parent.entity.game_objects.collisions.check_ground(point)
        if not collide:#there is no ground in front            
            return True
        return False         

    def on_giveup(self):#when giveup timer runs out
        self.parent.pop_child()#stop chasing

    def on_attack_cooldown(self):#when attack cooldown timer runs out
        self.attack_able = True      

class Hide(Idle):             
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.parent.entity.currentstate.handle_input('hide')

    def update(self):
        self.check_sight()

    def check_sight(self):
        if abs(self.parent.player_distance[0]) < self.parent.entity.hide_distance[0] and abs(self.parent.player_distance[1]) < self.parent.entity.hide_distance[1]:
            return True
        else:
            self.parent.pop_child()#player is away
            self.parent.entity.currentstate.handle_input('idle')
            return False

class Attack(Idle):
    def __init__(self, parent, **kwarg):
        super().__init__(parent)
        self.parent.entity.currentstate.handle_input('Attack')

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