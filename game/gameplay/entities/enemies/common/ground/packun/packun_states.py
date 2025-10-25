import sys

class EnemyStates():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self, dt):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def increase_phase(self):
        pass

    def handle_input(self, input):
        pass

    def modify_hit(self, effect):
        return effect

class Idle(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('idle')

    def update(self, dt):
        super().update(dt)
        self.entity.angle_state.check_sight()       
        self.check_attack()

    def check_attack(self):
        if abs(self.entity.currentstate.player_distance[0]) < self.entity.angle_state.attack_distance[0] and abs(self.entity.currentstate.player_distance[1]) < self.entity.angle_state.attack_distance[1]:
            if self.entity.flags['attack_able']:
                self.entity.flags['attack_able'] = False
                self.entity.game_objects.timer_manager.start_timer(100, self.entity.on_attack_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
                self.enter_state('Attack_pre')                      

class Attack_pre(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_pre')

    def increase_phase(self):#called from states, depending on if the player was close when it wanted to explode or not
        self.enter_state('Attack_main')

class Attack_main(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.attack()
        self.entity.animation.play('attack_main')

    def increase_phase(self):#called from states, depending on if the player was close when it wanted to explode or not
        self.enter_state('Idle')

class Death(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('death')

    def increase_phase(self):#called from states, depending on if the player was close when it wanted to explode or not
        self.entity.dead()

class Angle_sates():
    def __init__(self, entity):
        self.entity = entity      

    def check_sight(self):#called from currentstate, idle
        pass

    def get_angle(self):#called from attack of eneityt
        pass

class Up(Angle_sates):
    def __init__(self, entity):
        super().__init__(entity)
        self.angle = 0
        self.attack_distance = [250, 50]
                    
    def check_sight(self):
        if self.entity.currentstate.player_distance[0] > 0 and self.entity.dir[0] == -1 or self.entity.currentstate.player_distance[0] < 0 and self.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right            
            self.entity.dir[0] *= -1        

    def get_angle(self):
        return [self.entity.dir[0], -1], [5, 2]    

class Left(Angle_sates):
    def __init__(self, entity):
        super().__init__(entity)    
        self.angle = -90   
        self.attack_distance = [50, 250]

    def check_sight(self):
        if self.entity.currentstate.player_distance[1] > 0 and self.entity.dir[0] == 1 or self.entity.currentstate.player_distance[1] < 0 and self.entity.dir[0] == -1:#player on right and looking at left#player on left and looking right            
            self.entity.dir[0] *= -1    

    def get_angle(self):
        return [self.entity.dir[0], -self.entity.dir[0]], [2,5]

class Right(Angle_sates):
    def __init__(self, entity):
        super().__init__(entity)      
        self.angle = 90  
        self.attack_distance = [50, 250]

    def check_sight(self):
        if self.entity.currentstate.player_distance[1] > 0 and self.entity.dir[0] == -1 or self.entity.currentstate.player_distance[1] < 0 and self.entity.dir[0] == 1:#player on right and looking at left#player on left and looking right            
            self.entity.dir[0] *= -1    

    def get_angle(self):
        return [self.entity.dir[0], self.entity.dir[0]], [2,5]

class Down(Angle_sates):
    def __init__(self, entity):
        super().__init__(entity)
        self.angle = -180
        self.attack_distance = [250, 50]          
    
    def check_sight(self):
        if self.entity.currentstate.player_distance[0] > 0 and self.entity.dir[0] == 1 or self.entity.currentstate.player_distance[0] < 0 and self.entity.dir[0] == -1:#player on right and looking at left#player on left and looking right            
            self.entity.dir[0] *= -1    

    def get_angle(self):
        return [-self.entity.dir[0], 1], [5, 2]      