import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        #self.dir = self.entity.dir.copy()

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def increase_phase(self):#called when animation is finished in reset_timer
        pass

    def handle_input(self,input,**kwarg):
        pass

    def collide_entity_y(self,entity):                      
        if self.entity.velocity[1] < 0:#going up              
            entity.platform_physics.resolve_vertical_collision(self.entity, 'bottom')
        else:#going down
            entity.platform_physics.resolve_vertical_collision(self.entity, 'top')
        entity.body.update_rect_y()    

    def collide_y(self,entity):                    
        if entity.velocity[1] > self.entity.velocity[1]:#going down               
            entity.platform_physics.resolve_vertical_collision(self.entity, 'bottom')
            entity.platform_physics.limit_y()
        else:#going up
            entity.platform_physics.resolve_vertical_collision(self.entity, 'top')
        entity.body.update_rect_y()        

    def update(self, dt):
        pass

class Idle(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 0

    def update(self):
        self.time += self.entity.game_objects.game.dt
        self.entity.velocity = [0,0]
        if self.time > self.entity.frequency:
            self.enter_state('Go_down')

class Go_down(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.time = 0

    def update(self):
        self.entity.velocity[1] += self.entity.game_objects.game.dt 
        if abs(self.entity.hitbox.topleft[1] - self.entity.original_pos[1]) > self.entity.distance:
            self.entity.velocity[1] = 0
            self.enter_state('Down')

    def collide_entity_y(self,entity):     
        if self.entity.velocity[1] < 0:#going up              
            entity.platform_physics.resolve_vertical_collision(self.entity, 'bottom')
        else:#going down            
            self.entity.hole.on_collision(entity)
        entity.body.update_rect_y()    

class Down(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.time = 0

    def update(self):
        self.time += self.entity.game_objects.game.dt
        self.entity.velocity = [0,0]
        if self.time > self.entity.frequency:
            self.enter_state('Go_up')

class Go_up(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)

    def update(self):
        self.entity.velocity[1] -= self.entity.game_objects.game.dt 
        if abs(self.entity.hitbox.topleft[1] - self.entity.original_pos[1]) < 10:
            self.enter_state('Idle')          
