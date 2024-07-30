import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.center = self.entity.game_objects.camera.center.copy()

    def update(self):
        pass

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def init_pos(self):#called from camera when loading the map. It is to set correct center
        pass

    def increase_phase(self):
        pass     

class Idle_right(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] = self.entity.game_objects.map.PLAYER_CENTER[0] - self.entity.game_objects.player.rect[2]*0.5

    def update(self):
        distance = [self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if distance[0] < -self.entity.offset*16: return

        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_right')

class Stop_right(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] = self.entity.game_objects.game.window_size[0] - (self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx) - self.entity.game_objects.player.rect[2]*0.5
       
    def update(self):
        distance = [self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.center[0] = self.entity.game_objects.game.window_size[0] - (self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx) - self.entity.game_objects.player.rect[2]*0.5
        else:
            self.enter_state('Idle_right')

class Idle_left(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] =  self.entity.game_objects.map.PLAYER_CENTER[0] - self.entity.game_objects.player.rect[2]*0.5

    def update(self):
        distance = [self.entity.rect.right - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if distance[0] > self.entity.offset*16: return

        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_left')

class Stop_left(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] =  self.entity.game_objects.player.hitbox.centerx - self.entity.rect.right - self.entity.game_objects.player.rect[2]*0.5

    def update(self):
        distance = [self.entity.rect.right - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.center[0] =  self.entity.game_objects.player.hitbox.centerx - self.entity.rect.right - self.entity.game_objects.player.rect[2]*0.5
        else:
            self.enter_state('Idle_left')

class Idle_bottom(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        #self.entity.game_objects.camera.center[1] = self.entity.game_objects.map.PLAYER_CENTER[1] - self.entity.game_objects.player.rect[3]*0.5# should only be set if there is no other stop bottom working in aila

    def update(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.top - self.entity.game_objects.player.hitbox.centery]                                   
        if distance[1] < -self.entity.offset*16: return

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_bottom')

class Stop_bottom(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.determine_sign()
        self.true_center = self.center.copy()
        self.entity.game_objects.camera.stop_handeler.add_stop('bottom')

    def init_pos(self):#called from map loader
        self.entity.game_objects.camera.center[1] = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - self.entity.game_objects.player.hitbox.centery) - self.entity.game_objects.player.rect[3]*0.5
        self.center = self.entity.game_objects.camera.center.copy()
        self.sign = 1

    def determine_sign(self):
        target = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - (self.entity.game_objects.player.hitbox.centery - self.entity.game_objects.player.velocity[1]*2)) - self.entity.game_objects.player.rect[3]*0.5
        if self.center[1] > target:
            self.sign = 1#from up to down
        else:
            self.sign = -1#from down to up

    def update(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.top - self.entity.game_objects.player.hitbox.centery]

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            target = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - self.entity.game_objects.player.hitbox.centery) - self.entity.game_objects.player.rect[3]*0.5
            self.true_center[1] -= (self.entity.game_objects.camera.center[1]-target)*(0.03 - self.sign*0.01)
            self.center[1] = int(self.true_center[1])
            #self.center[1] -= self.sign*3#self.sign*(abs(self.entity.game_objects.camera.center[1]-target))*0.1
            self.entity.game_objects.camera.center[1] = self.sign*max(self.sign*target,self.sign*self.center[1])#when sign is negative, it works as min
        else:
            self.entity.game_objects.camera.stop_handeler.remove_stop('bottom')
            self.enter_state('Idle_bottom')

class Idle_top(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        #self.entity.game_objects.camera.center[1] = self.entity.game_objects.map.PLAYER_CENTER[1] - self.entity.game_objects.player.rect[3]*0.5

    def update(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.bottom - self.entity.game_objects.player.hitbox.centery]
        if distance[1] > self.entity.offset*16: return

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_top')

class Stop_top(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.true_center = self.center.copy()        
        #self.entity.game_objects.camera.center[1] = self.entity.game_objects.player.hitbox.centery - self.entity.rect.bottom - self.entity.game_objects.player.rect[3]*0.5
        self.entity.game_objects.camera.stop_handeler.add_stop('top')

    def update(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.bottom - self.entity.game_objects.player.hitbox.centery] 

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            target = self.entity.game_objects.player.hitbox.centery - self.entity.rect.bottom - self.entity.game_objects.player.rect[3]*0.5
            #self.true_center[1] -= (self.entity.game_objects.camera.center[1] - target)*0.03
            self.entity.game_objects.camera.center[1] = target                    
        else:
            self.entity.game_objects.camera.stop_handeler.remove_stop('top')
            self.enter_state('Idle_top')

class Idle_center(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)

    def update(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx, self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]

        if abs(distance[0]) < 10:
            self.enter_state('Stop_center')        

class Stop_center(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera.stop_handeler.add_stop('center')

    def update(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[0]) > self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.stop_handeler.remove_stop('center')
            self.enter_state('Idle_center')
        else:
            self.entity.game_objects.camera.center[0] = self.entity.game_objects.player.hitbox.centerx - (48 + self.entity.rect.centerx - self.entity.game_objects.game.window_size[0]*0.5)

            #self.entity.game_objects.camera.center[1] = self.entity.game_objects.player.hitbox.centery - (self.entity.rect.centery - self.entity.game_objects.game.window_size[1]*0.5)

            
        