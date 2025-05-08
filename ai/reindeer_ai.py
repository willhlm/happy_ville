import sys

def sign(number):
    if number > 0: return 1
    elif number < 0: return -1
    else: return 0

class AI():#manager
    def __init__(self, entity):
        self.entity = entity
        self.task_queue = []  # Tasks to execute in order
        self.phase = 1  # Track the current phase of the boss fight
        self.state = Idle(self.entity)

    def activate(self):
        self.state = Chase(self.entity)

    def deactivate(self):
        self.state = Idle(self.entity)

    def update(self):
        self.track_player_distance()
        self.state.update()

    def track_player_distance(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx, self.entity.game_objects.player.rect.centery - self.entity.rect.centery]

    def start_next_task(self):#called when animation/state is finished
        if self.task_queue:
            kwarg = self.task_queue.pop(0)
            self.state = getattr(sys.modules[__name__], kwarg['task'].capitalize())(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def queue_task(self, **kwarg):
        self.task_queue.append(kwarg)

    def change_phase(self, phase):
        self.phase = phase
        self.task_queue.clear()  # Clear current tasks

    def handle_input(self, input):
        pass

class AI_states():
    def __init__(self, entity, **kwarg):
        self.entity = entity
    
    def update(self):
        pass

class Idle(AI_states):#do nothing
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   

class Wait(AI_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.duration = kwarg.get('duration',50)

    def update(self):   
        self.duration -= self.entity.game_objects.game.dt  
        if self.duration < 0:
            self.entity.AI.start_next_task()

class Turn_around(AI_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.dir[0] *= -1

    def update(self):   
        self.entity.AI.start_next_task()

class Attack(AI_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.currentstate.handle_input('attack')#tell animation
        self.entity.flags['attack_able'] = False   

    def animation_finish(self):#called from reinder_states
        self.entity.AI.start_next_task()           

class Charge(AI_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.currentstate.handle_input('charge')#tell animation        

    def animation_finish(self):#called from reinder_states
        self.entity.AI.start_next_task()  

class Chase(AI_states):            
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.timer = self.entity.game_objects.timer_manager.start_timer(150, self.out_of_range, 'reindeer_range')       

    def update(self):   
        self.check_sight()
        self.entity.chase([0,0])#chases at self.entity.dir direction

    def check_sight(self):               
        if self.entity.AI.player_distance[0] > 0 and self.entity.dir[0] == -1 or self.entity.AI.player_distance[0] < 0 and self.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right            
            self.entity.AI.queue_task(task = 'wait', duration = 20)  
            self.entity.AI.queue_task(task = 'turn_around')
            self.entity.AI.queue_task(task = 'wait', duration = 20)  
            self.entity.AI.queue_task(task = 'chase')
            self.entity.AI.start_next_task()
            self.entity.game_objects.timer_manager.remove_timer(self.timer)

        elif abs(self.entity.AI.player_distance[0]) < self.entity.attack_distance[0] and abs(self.entity.AI.player_distance[1]) < self.entity.attack_distance[1]:#player close             
            if self.entity.flags['attack_able']:
                self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
                self.entity.AI.queue_task(task = 'attack')
                self.entity.AI.queue_task(task = 'wait', duration = 20)  
                self.entity.AI.queue_task(task = 'chase')
                self.entity.AI.start_next_task()
                self.entity.game_objects.timer_manager.remove_timer(self.timer)

        elif abs(self.entity.AI.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.entity.AI.player_distance[1]) > self.entity.aggro_distance[1]:#player far away                 
            pass

        elif abs(self.entity.AI.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.entity.AI.player_distance[1]) < self.entity.aggro_distance[1]:#player within aggro range                           
            self.timer.reset()

    def out_of_range(self):#called when player has been out of aggro range for a while
        self.entity.AI.queue_task(task = 'charge')  
        self.entity.AI.queue_task(task = 'wait', duration = 20)  
        self.entity.AI.queue_task(task = 'chase') 
        self.entity.AI.start_next_task()    
