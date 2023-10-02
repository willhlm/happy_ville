import sys

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.update_state()

    def handle_input(self,input):
        pass

class Idle_right(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] = self.entity.game_objects.map.PLAYER_CENTER[0] - self.entity.game_objects.player.rect[2]*0.5

    def update_state(self):
        distance = [self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if distance[0] < -self.entity.offset*16: return

        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_right')

class Stop_right(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] = self.entity.game_objects.game.window_size[0] - (self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx) - self.entity.game_objects.player.rect[2]*0.5

    def update_state(self):
        distance = [self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.center[0] = self.entity.game_objects.game.window_size[0] - (self.entity.rect.left - self.entity.game_objects.player.hitbox.centerx) - self.entity.game_objects.player.rect[2]*0.5
        else:
            self.enter_state('Idle_right')

class Idle_left(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] = self.entity.game_objects.map.PLAYER_CENTER[0] - self.entity.game_objects.player.rect[2]*0.5

    def update_state(self):
        distance = [self.entity.rect.right - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if distance[0] > self.entity.offset*16: return

        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_left')

class Stop_left(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[0] =  self.entity.game_objects.player.hitbox.centerx - self.entity.rect.right - self.entity.game_objects.player.rect[2]*0.5

    def update_state(self):
        distance = [self.entity.rect.right - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.centery - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[1]) < self.entity.size[1]*0.5 and abs(distance[0]) < self.entity.game_objects.game.window_size[0]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.center[0] =  self.entity.game_objects.player.hitbox.centerx - self.entity.rect.right - self.entity.game_objects.player.rect[2]*0.5
        else:
            self.enter_state('Idle_left')

class Idle_bottom(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[1] = self.entity.game_objects.map.PLAYER_CENTER[1] - self.entity.game_objects.player.rect[3]*0.5

    def update_state(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.top - self.entity.game_objects.player.hitbox.centery]
        if distance[1] < -self.entity.offset*16: return

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_bottom')

class Stop_bottom(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[1] = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - self.entity.game_objects.player.hitbox.centery) - self.entity.game_objects.player.rect[3]*0.5

    def update_state(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.top - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.center[1] = self.entity.game_objects.game.window_size[1] - (self.entity.rect.top - self.entity.game_objects.player.hitbox.centery) - self.entity.game_objects.player.rect[3]*0.5
        else:
            self.enter_state('Idle_bottom')

class Idle_top(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[1] = self.entity.game_objects.map.PLAYER_CENTER[1] - self.entity.game_objects.player.rect[3]*0.5

    def update_state(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.bottom - self.entity.game_objects.player.hitbox.centery]
        if distance[1] > self.entity.offset*16: return

        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.enter_state('Stop_top')

class Stop_top(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.camera.center[1] = self.entity.game_objects.player.hitbox.centery - self.entity.rect.bottom - self.entity.game_objects.player.rect[3]*0.5

    def update_state(self):
        distance = [self.entity.rect.centerx - self.entity.game_objects.player.hitbox.centerx,self.entity.rect.bottom - self.entity.game_objects.player.hitbox.centery]
        if abs(distance[0]) < self.entity.size[0]*0.5 and abs(distance[1]) < self.entity.game_objects.game.window_size[1]*0.5:#if on screen on y and coser than half screen on x
            self.entity.game_objects.camera.center[1] = self.entity.game_objects.player.hitbox.centery - self.entity.rect.bottom - self.entity.game_objects.player.rect[3]*0.5
        else:
            self.enter_state('Idle_top')

class Idle_center(Basic_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.game_objects.camera.center[0] = self.entity.game_objects.player.hitbox.centerx - (self.entity.rect.centerx - self.entity.game_objects.game.window_size[0]*0.5)
        self.entity.game_objects.camera.center[1] = self.entity.game_objects.player.hitbox.centery - (self.entity.rect.centery - self.entity.game_objects.game.window_size[1]*0.5)
