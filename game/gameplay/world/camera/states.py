import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity
        self.center = self.entity.game_objects.camera_manager.camera.center.copy()
        self.y_offset = self.entity.game_objects.camera_manager.camera.y_offset

    def update(self, dt):
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
        #self.entity.game_objects.camera_manager.camera.center[0] = self.entity.game_objects.map.PLAYER_CENTER[0] #- self.entity.game_objects.player.rect[2]*0.5

    def update(self, dt):
        distance = [self.entity.rect.left - self.entity.game_objects.player.true_pos[0],self.entity.rect.centery - self.entity.game_objects.player.true_pos[1]]
        if distance[0] < -self.entity.offset*16: return

        if abs(distance[1]) < self.entity.size[1] and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5 +  self.entity.game_objects.player.rect[2]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_right')

class Stop_right(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera_manager.camera.center[0] = self.entity.game_objects.game.window_size[0] - (self.entity.rect.left - self.entity.game_objects.player.true_pos[0])# - self.entity.game_objects.player.rect[2]*0.5

    def update(self, dt):
        distance = [self.entity.rect.left - self.entity.game_objects.player.true_pos[0], self.entity.rect.centery - self.entity.game_objects.player.true_pos[1]]
        if abs(distance[1]) < self.entity.size[1] and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5 + self.entity.game_objects.player.rect[2]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera_manager.camera.target[0] = self.entity.game_objects.game.window_size[0] - (self.entity.rect.left - self.entity.game_objects.player.true_pos[0])# + self.entity.game_objects.player.rect[2]*0.5
            self.entity.game_objects.camera_manager.camera.center[0] = self.entity.game_objects.camera_manager.camera.target[0]
        else:
            self.enter_state('Idle_right')

class Idle_left(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        #self.entity.game_objects.camera_manager.camera.center[0] =  self.entity.game_objects.map.PLAYER_CENTER[0] - self.entity.game_objects.player.rect[2]*0.5

    def update(self, dt):        
        distance = [self.entity.rect.right - self.entity.game_objects.player.true_pos[0] - self.entity.game_objects.player.rect[2]*0.5, self.entity.rect.centery - self.entity.game_objects.player.true_pos[1]]

        if distance[0] > self.entity.offset*16: return        

        if abs(distance[1]) < self.entity.size[1] and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5: #- self.entity.game_objects.player.rect[2]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_left')

class Stop_left(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera_manager.camera.center[0] =  self.entity.game_objects.player.true_pos[0] - self.entity.rect.right #- self.entity.game_objects.player.rect[2]*0.5

    def update(self, dt):  
        distance = [self.entity.rect.right - self.entity.game_objects.player.true_pos[0],self.entity.rect.centery - self.entity.game_objects.player.true_pos[1]]
        if abs(distance[1]) < self.entity.size[1] and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5 - self.entity.game_objects.player.rect[2]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera_manager.camera.target[0] = self.entity.game_objects.player.true_pos[0] - self.entity.rect.right #- self.entity.game_objects.player.rect[2] * 0.5
            self.entity.game_objects.camera_manager.camera.center[0] = self.entity.game_objects.camera_manager.camera.target[0]
        else:
            self.enter_state('Idle_left')

class Idle_bottom(Basic_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        #self.entity.game_objects.camera_manager.camera.center[1] = self.entity.game_objects.map.PLAYER_CENTER[1] - self.entity.game_objects.player.rect[3]*0.5# should only be set if there is no other stop bottom working in aila

    def update(self, dt):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.top - self.entity.game_objects.player.hitbox.centery]
        if distance[1] < -self.entity.offset*16: return

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5 + self.y_offset:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_bottom')

class Stop_bottom(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.determine_sign()
        self.true_center = self.center.copy()
        self.entity.game_objects.camera_manager.stop_handeler.add_stop('bottom')

    def init_pos(self):#called from map loader
        self.entity.game_objects.camera_manager.camera.center[1] = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - self.entity.game_objects.player.hitbox.centery) - self.entity.game_objects.player.rect[3]*0.5 - self.entity.rect[3]
        self.center = self.entity.game_objects.camera_manager.camera.center.copy()
        self.sign = 1

    def determine_sign(self):
        target = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - (self.entity.game_objects.player.hitbox.centery - self.entity.game_objects.player.velocity[1]*2)) - self.entity.game_objects.player.rect[3]*0.5
        if self.center[1] > target:
            self.sign = 1#from up to down
        else:
            self.sign = -1#from down to up

    def update(self, dt):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx, self.entity.rect.top - self.entity.game_objects.player.hitbox.centery]

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5 + self.y_offset:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera_manager.camera.target[1] = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - self.entity.game_objects.player.hitbox.centery) - self.entity.game_objects.player.rect[3] + self.entity.rect[3]
            self.true_center[1] -= (self.entity.game_objects.camera_manager.camera.center[1] - self.entity.game_objects.camera_manager.camera.target[1]) * (0.03 - self.sign * 0.01)
            self.center[1] = int(self.true_center[1])
            self.entity.game_objects.camera_manager.camera.center[1] = self.sign * max(self.sign * self.entity.game_objects.camera_manager.camera.target[1], self.sign * self.center[1])#when sign is negative, it works as min
        else:
            self.entity.game_objects.camera_manager.stop_handeler.remove_stop('bottom')
            self.enter_state('Idle_bottom')

class Idle_top(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        #self.entity.game_objects.camera_manager.camera.center[1] = self.entity.game_objects.map.PLAYER_CENTER[1] - self.entity.game_objects.player.rect[3]*0.5

    def update(self, dt):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.true_pos[0],self.entity.rect.bottom - self.entity.game_objects.player.true_pos[1]]
        if distance[1] > self.entity.offset*16: return

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5 + self.y_offset:#if on screen on y and closer than half screen on x
            self.enter_state('Stop_top')

class Stop_top(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.true_center = self.center.copy()
        #self.entity.game_objects.camera_manager.camera.center[1] = self.entity.game_objects.player.hitbox.centery - self.entity.rect.bottom - self.entity.game_objects.player.rect[3]*0.5
        self.entity.game_objects.camera_manager.stop_handeler.add_stop('top')

    def update(self, dt):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.true_pos[0],self.entity.rect.bottom - self.entity.game_objects.player.true_pos[1]]

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5 + self.y_offset - self.entity.game_objects.player.rect[3] * 0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera_manager.camera.target[1] = self.entity.game_objects.player.true_pos[1] - self.entity.rect.bottom #+ self.entity.game_objects.player.rect[3] * 0.5 - self.entity.rect[3]
            #self.true_center[1] -= (self.entity.game_objects.camera_manager.camera.center[1] - target)*0.03
            self.entity.game_objects.camera_manager.camera.center[1] = self.entity.game_objects.camera_manager.camera.target[1]
        else:
            self.entity.game_objects.camera_manager.stop_handeler.remove_stop('top')
            self.enter_state('Idle_top')

class Idle_center(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)

    def update(self, dt):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.true_pos[0], self.entity.rect.centery - self.entity.game_objects.player.true_pos[1]]

        #if abs(distance[0]) < 10:
        if abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:
            self.enter_state('Stop_center')

class Stop_center(Basic_states):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.entity.game_objects.camera_manager.stop_handeler.add_stop('center')

    def update(self, dt):#TODO also vertical
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.true_pos[0],self.entity.rect.centery - self.entity.game_objects.player.true_pos[1]]
        if abs(distance[0]) > self.entity.game_objects.game.window_size[0]*0.5 or abs(distance[1]) > self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera_manager.stop_handeler.remove_stop('center')
            self.enter_state('Idle_center')
        else:
            self.entity.game_objects.camera_manager.camera.target[0] = self.entity.game_objects.player.true_pos[0] - (self.entity.game_objects.player.rect[2]*0.5 + self.entity.rect.centerx - self.entity.game_objects.game.window_size[0]*0.5)

            scale = 10#need to be high so that aila doesn't move ftaser than scroll
            if distance[0] < 0:
                self.center[0] += dt * scale
                self.entity.game_objects.camera_manager.camera.center[0] = min(self.entity.game_objects.camera_manager.camera.target[0], self.center[0])
                self.center[0] = min(self.entity.game_objects.camera_manager.camera.center[0], self.center[0])
            else:
                self.center[0] -= dt * scale
                self.entity.game_objects.camera_manager.camera.center[0] = max(self.entity.game_objects.camera_manager.camera.target[0], self.center[0])
                self.center[0] = max(self.entity.game_objects.camera_manager.camera.center[0], self.center[0])

           # self.entity.game_objects.camera_manager.camera.center[0] = target
            #self.entity.game_objects.camera_manager.camera.center[1] = self.entity.game_objects.player.hitbox.centery - (self.entity.rect.centery - self.entity.game_objects.game.window_size[1]*0.5)
