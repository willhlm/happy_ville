from utils import register_state

#attack patterns
PATTERNS = {
    "combo_slash": {
        "weight": 4,
        "range": "close",
        "tasks": [
            {"task": "attack_pre"},
            {"task": "attack_main"},
            {"task": "wait", "duration": 20},
            {"task": "think"},
        ]
    },
    "jump_and_slam": {
        "weight": 3,
        "range": "mid",
        "tasks": [
            {"task": "jump_pre"},
            {"task": "jump_main"},
            {"task": "fall_pre"},
            {"task": "fall_main"},
            {"task": "slam_pre"},
            {"task": "slam_main"},
            {"task": "slam_post"},
            {"task": "wait", "duration": 80},
            {"task": "think"}
        ]
    },
    "charge_combo": {
        "weight": 2,
        "range": "far",
        "tasks": [
            {"task": "charge_pre"},
            {"task": "charge_main"},
            {"task": "charge_run"},
            {"task": "charge_attack_pre"},
            {"task": "charge_attack"},
            {"task": "charge_post"},
            {"task": "wait", "duration": 30},
            {"task": "think"}
        ]
    },
    "retreat_then_jump": {
        "weight": 1,
        "range": "any",  # Flexible
        "tasks": [
            {"task": "wait", "duration": 15},
            {"task": "turn_around"},
            {"task": "wait", "duration": 15},
            {"task": "jump_pre"},
            {"task": "jump_main"},
            {"task": "fall_pre"},
            {"task": "fall_main"},
            {"task": "think"}
        ]
    }
}

STATE_REGISTRY = {}#populate with register_state decorator

class Base_states():
    def __init__(self, entity, **kwarg):
        self.entity = entity
    
    def update(self):
        pass

    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

@register_state(STATE_REGISTRY)
class Idle(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        animation = kwarg.get('animation', 'idle_nice')
        self.entity.animation.play(animation)

@register_state(STATE_REGISTRY)
class Wait(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.animation.play('idle')
        self.duration = kwarg.get('duration',50)

    def update(self):   
        self.duration -= self.entity.game_objects.game.dt  
        if self.duration < 0:
            self.entity.currentstate.start_next_task()

@register_state(STATE_REGISTRY)
class Turn_around(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.dir[0] *= -1
        self.entity.animation.play('idle')                  

    def update(self):
        self.entity.currentstate.start_next_task()

@register_state(STATE_REGISTRY)
class Transform(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('transform')

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.currentstate.start_next_task()      

@register_state(STATE_REGISTRY)
class Move(Base_states):#not used
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('walk')
        self.timer = 200  # duration to walk before re-evaluating (adjust as needed)

    def update(self):
        self.entity.chase([0, 0])

        dist_x, dist_y = self.entity.currentstate.player_distance
        self.timer -= self.entity.game_objects.game.dt

        # Stop if close enough to reevaluate
        if abs(dist_x) < self.entity.attack_distance[0] * 1.5:
            self.entity.currentstate.queue_task(task='think')
            self.entity.currentstate.start_next_task()

        elif self.timer <= 0:
            self.entity.currentstate.queue_task(task='think')  # reevaluate after some walk
            self.entity.currentstate.start_next_task()

@register_state(STATE_REGISTRY)
class Think(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)        

    def update(self):
        dist_x, dist_y = self.entity.currentstate.player_distance

        # Face the player first
        if (dist_x > 0 and self.entity.dir[0] == -1) or (dist_x < 0 and self.entity.dir[0] == 1):
            self.entity.currentstate.queue_task(task="wait", duration=20)
            self.entity.currentstate.queue_task(task="turn_around")
            self.entity.currentstate.queue_task(task="wait", duration=20)
            self.entity.currentstate.queue_task(task="think")
            self.entity.currentstate.start_next_task()
            return

        if self.entity.flags["attack_able"]:
            pattern = self.entity.currentstate.selector.pick_pattern(dist_x, dist_y)
            self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)
            for step in pattern["tasks"]:
                self.entity.currentstate.queue_task(**step)
            self.entity.currentstate.start_next_task()
            return

        # fallback wait
        self.entity.currentstate.queue_task(task="wait", duration=40)
        self.entity.currentstate.queue_task(task="think")
        self.entity.currentstate.start_next_task()

@register_state(STATE_REGISTRY)
class Roar_pre(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('roar_pre')

    def increase_phase(self):
        self.entity.currentstate.start_next_task()

@register_state(STATE_REGISTRY)
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

@register_state(STATE_REGISTRY)
class Roar_post(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('roar_post')

    def increase_phase(self):
        self.entity.currentstate.start_next_task()     

@register_state(STATE_REGISTRY)
class Death(Base_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.animation.play('death')

    def update(self):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.currentstate.queue_task(task = 'Dead')
        self.entity.currentstate.start_next_task()  #got to death

@register_state(STATE_REGISTRY)
class Dead(Base_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.animation.play('dead') 
        self.entity.dead()

@register_state(STATE_REGISTRY)
class Attack_pre(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_pre')
        self.entity.flags['attack_able'] = False   

    def increase_phase(self):
         self.entity.currentstate.start_next_task()     

@register_state(STATE_REGISTRY)
class Attack_main(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_main')
        attack = self.entity.attack(self.entity, lifetime = 10)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.entity.currentstate.start_next_task()     

@register_state(STATE_REGISTRY)
class Charge_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)   
        self.entity.animation.play('charge_pre')
        self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)     

    def increase_phase(self):
        self.entity.currentstate.start_next_task()    

@register_state(STATE_REGISTRY)
class Charge_main(Base_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)       
        self.entity.animation.play('charge_main') 
        self.cycles = 3       

    def increase_phase(self):
        self.cycles -= 1
        if self.cycles == 0: self.entity.currentstate.start_next_task()    

@register_state(STATE_REGISTRY)
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

    def handle_input(self, input):
        if input == 'Wall':
            self.entity.currentstate.start_next_task()

@register_state(STATE_REGISTRY)
class Charge_attack_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_attack_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()  

@register_state(STATE_REGISTRY)
class Charge_attack(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_attack') 
        attack = self.entity.attack(self.entity, lifetime = 10)#make the object
        self.entity.projectiles.add(attack)#add to group but in main phase

    def increase_phase(self):
        self.entity.currentstate.start_next_task()        

@register_state(STATE_REGISTRY)
class Charge_post(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('charge_post') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()          

@register_state(STATE_REGISTRY)
class Jump_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()            

@register_state(STATE_REGISTRY)
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

@register_state(STATE_REGISTRY)
class Fall_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('fall_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()       

@register_state(STATE_REGISTRY)
class Fall_main(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('fall_main') 

    def handle_input(self, input):
        if input == 'Ground':
            self.entity.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)     
            self.entity.acceleration[0] =0
            self.entity.currentstate.start_next_task()   
            
@register_state(STATE_REGISTRY)            
class Slam_pre(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('slam_pre') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()   

@register_state(STATE_REGISTRY)
class Slam_main(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('slam_main') 
        self.entity.slam_attack()

    def increase_phase(self):
        self.entity.currentstate.start_next_task()           

@register_state(STATE_REGISTRY)
class Slam_post(Base_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('slam_post') 

    def increase_phase(self):
        self.entity.currentstate.start_next_task()             