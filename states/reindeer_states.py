import sys

def pattern_normal_phase():#not used: if we want repeated pattern with phases
    return [
        {'task': 'idle', 'duration': 1000, 'repeat': True},
        {'task': 'slam', 'power': 1, 'repeat': True},
        {'task': 'recover', 'duration': 500, 'repeat': True}
    ]

def pattern_rage_phase():#not used: if we want repeated pattern with phases
    return [
        {'task': 'idle', 'duration': 600, 'repeat': True},
        {'task': 'rage_slam', 'power': 2, 'repeat': True},
        {'task': 'teleport', 'target': 'random', 'repeat': True}
    ]    

class State_manager():#manager
    def __init__(self, entity):
        self.entity = entity
        self.task_queue = []  # Tasks to execute in order
        self.state = Idle(self.entity)

    def update(self):
        self.track_player_distance()
        self.state.update()

    def track_player_distance(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx, self.entity.game_objects.player.rect.centery - self.entity.rect.centery]

    def start_next_task(self):#start when state is finished
        if self.task_queue:
            kwarg = self.task_queue.pop(0)
            self.state = getattr(sys.modules[__name__], kwarg['task'].capitalize())(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

            if kwarg.pop("repeat", False):#re-add the task if repeat=True
                self.queue_task(**kwarg)

    def queue_task(self, **kwarg):
        self.task_queue.append(kwarg)

    def clear_tasks(self):
        self.task_queue.clear()  # Clear current tasks

    def handle_input(self, input):
        self.state.handle_input(input)
    
    def increase_phase(self):
        self.state.increase_phase()

class Base_states():
    def __init__(self, entity, **kwarg):
        self.entity = entity
    
    def update(self):
        pass

    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

class Idle(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        animation = kwarg.get('animation', 'idle_nice')
        self.entity.animation.play(animation)

class Wait(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.animation.play('idle')
        self.duration = kwarg.get('duration',50)

    def update(self):   
        self.duration -= self.entity.game_objects.game.dt  
        if self.duration < 0:
            self.entity.currentstate.start_next_task()

class Turn_around(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.animation.play('idle')
        self.entity.dir[0] *= -1

    def update(self):   
        self.entity.currentstate.start_next_task()

class Transform(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('transform')

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.currentstate.start_next_task()      

class Chase(Base_states):            
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.animation.play('walk')

    def update(self):   
        self.check_sight()        

    def check_sight(self):    
        if self.entity.currentstate.player_distance[0] > 0 and self.entity.dir[0] == -1 or self.entity.currentstate.player_distance[0] < 0 and self.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right            
            self.entity.currentstate.queue_task(task = 'wait', duration = 20)  
            self.entity.currentstate.queue_task(task = 'turn_around')
            self.entity.currentstate.queue_task(task = 'wait', duration = 20)  
            self.entity.currentstate.queue_task(task = 'chase')
            self.entity.currentstate.start_next_task()

        if abs(self.entity.currentstate.player_distance[0]) < self.entity.attack_distance[0] and abs(self.entity.currentstate.player_distance[1]) < self.entity.attack_distance[1]:#player close             
            if self.entity.flags['attack_able']:
                self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
                self.entity.currentstate.queue_task(task = 'attack_pre')
                self.entity.currentstate.queue_task(task = 'attack_main')
                self.entity.currentstate.queue_task(task = 'wait', duration = 20)  
                self.entity.currentstate.queue_task(task = 'chase')
                self.entity.currentstate.start_next_task()

        elif abs(self.entity.currentstate.player_distance[0]) < self.entity.chase_distance[0] and abs(self.entity.currentstate.player_distance[1]) < self.entity.chase_distance[1]:#player close             
            self.entity.chase([0,0])#chases at self.entity.dir direction

        elif abs(self.entity.currentstate.player_distance[0]) < self.entity.jump_distance[0] and abs(self.entity.currentstate.player_distance[1]) < self.entity.jump_distance[1]:#player far away                 
            self.entity.currentstate.queue_task(task = 'jump_pre')  
            self.entity.currentstate.queue_task(task = 'jump_main')  
            self.entity.currentstate.queue_task(task = 'fall_pre')  
            self.entity.currentstate.queue_task(task = 'fall_main')  
            self.entity.currentstate.queue_task(task = 'slam_pre')  
            self.entity.currentstate.queue_task(task = 'slam_main')  
            self.entity.currentstate.queue_task(task = 'slam_post')  
            self.entity.currentstate.queue_task(task = 'wait', duration = 100)  
            self.entity.currentstate.queue_task(task = 'chase')  
            self.entity.currentstate.start_next_task()    

        else:
            self.entity.currentstate.queue_task(task = 'charge_pre')  
            self.entity.currentstate.queue_task(task = 'charge_main')  
            self.entity.currentstate.queue_task(task = 'charge_run')  
            self.entity.currentstate.queue_task(task = 'charge_attack_pre')  
            self.entity.currentstate.queue_task(task = 'charge_attack')  
            self.entity.currentstate.queue_task(task = 'charge_post')          
            self.entity.currentstate.queue_task(task = 'wait', duration = 20)  
            self.entity.currentstate.queue_task(task = 'chase') 
            self.entity.currentstate.start_next_task()  

class Roar_pre(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('roar_pre')

    def increase_phase(self):
        self.entity.currentstate.start_next_task()

class Roar_main(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('roar_main')
        self.entity.game_objects.camera_manager.camera_shake(amp = 3, duration = 100)#amplitude, duration
        center = [self.entity.rect.centerx-self.entity.game_objects.camera_manager.camera.scroll[0],self.entity.rect.centery-self.entity.game_objects.camera_manager.camera.scroll[1]]
        self.entity.game_objects.shader_render.append_shader('Speed_lines', center = center)
        self.cycles = 7

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles == 0: 
            self.entity.currentstate.start_next_task()    
            self.entity.game_objects.shader_render.remove_shader('Speed_lines')

class Roar_post(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('roar_post')

    def increase_phase(self):
        self.entity.currentstate.start_next_task()     

class Death(Base_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.currentstate.start_next_task()  #got to death

class Dead(Base_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.dead()

    def update(self):
        self.entity.velocity = [0,0]

class Attack_pre(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_pre')
        self.entity.flags['attack_able'] = False   

    def increase_phase(self):
         self.entity.currentstate.start_next_task()     

class Attack_main(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_main')
        attack = self.entity.attack(self.entity, lifetime = 10)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.entity.currentstate.start_next_task()     

class Charge_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.animation.play('charge_pre')
        self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)     

    def increase_phase(self):
        self.entity.currentstate.start_next_task()    

class Charge_main(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)       
        self.entity.animation.play('charge_main') 
        self.cycles = 3       

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles == 0: self.entity.currentstate.start_next_task()    

class Charge_run(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_run') 
        self.cycles = 1#to add a delay from running to attack
        self.next = False#to add a delay from running to attack

    def update(self):
        self.entity.velocity[0] = self.entity.dir[0] * 5
        if abs(self.entity.currentstate.player_distance[0]) < self.entity.attack_distance[0]:    
            self.next = True

    def increase_phase(self):
        if not self.next: return
        self.cycles -= 1 
        if self.cycles == 0: self.entity.currentstate.start_next_task()

class Charge_attack_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_attack_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()  

class Charge_attack(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_attack') 
        attack = self.entity.attack(self.entity, lifetime = 10)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.entity.currentstate.start_next_task()        

class Charge_post(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_post') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()          

class Jump_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()            

class Jump_main(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_main') 
        self.timer = 5      
        self.entity.acceleration[0] = 1

    def update(self):
        self.timer -= self.entity.game_objects.game.dt
        self.entity.velocity[1] = -7           
        if self.timer < 0:
            self.entity.currentstate.start_next_task()    

class Fall_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('fall_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()       

class Fall_main(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('fall_main') 

    def handle_input(self, input):
        if input == 'Ground':
            self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)     
            self.entity.acceleration[0] =0
            self.entity.currentstate.start_next_task()   
            
class Slam_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('slam_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()   

class Slam_main(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('slam_main') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()           

class Slam_post(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('slam_post') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()             