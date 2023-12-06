import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity

    def enter_AI(self, newAI, **kwarg):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def deactivate(self):#called when health < 0
        self.enter_AI('Idle')

    def activate(self):#called when cutscene is finished or when aila attacks
        self.enter_AI('Aggro')

    def update(self):
        pass

class Idle(AI):#do nothing
    def __init__(self,entity):
        super().__init__(entity)

class Aggro(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        value = random.randint(0,100)
        if value ==1:
            if self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx > 0:
                self.enter_AI('Fly_attack',dir = [1,0],number=2)
            else:
                self.enter_AI('Fly_attack',dir = [-1,0],number=2)
        elif value == 2:
            pass

class Teleport(AI):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.number = kwarg['number']
        self.entity.currentstate.enter_state('Blink_pre')

    def teleport(self):#called from states
        self.number -= 1
        x = random.randint(self.entity.game_objects.camera.scroll[0]+self.entity.rect[2],self.entity.game_objects.game.window_size[0] + self.entity.game_objects.camera.scroll[0]-self.entity.rect[2])
        y = random.randint(self.entity.game_objects.camera.scroll[1]+self.entity.rect[3],self.entity.game_objects.game.window_size[1] + self.entity.game_objects.camera.scroll[1]-self.entity.rect[3])
        self.entity.true_pos = [x,y]

    def finish(self):#caleld when animation is finished from states
        if self.number == 0:
            self.enter_AI('Wait',count = 100,next_state = 'Aggro')
        else:
            self.entity.currentstate.enter_state('Blink_pre')

class Fly_attack(AI):
    def __init__(self,entity,**kwarg):
        super().__init__(entity)
        self.dir = kwarg['dir']
        self.entity.dir[0] = self.dir[0]
        self.number = kwarg['number']

    def update(self):
        self.entity.velocity[0] += self.dir[0]*2*self.entity.game_objects.game.dt
        pos = self.entity.true_pos[0] - self.entity.game_objects.camera.scroll[0]

        if self.dir[0] > 0:
            if pos > self.entity.game_objects.game.window_size[0]:#outisde screens
                self.next_phase()
        else:#if negative
            if pos < -150:#outisde screens
                self.next_phase()

    def next_phase(self):
        self.number -= 1
        if self.number == 0:
            self.enter_AI('Teleport', number = 2)
        else:
            self.entity.true_pos[1] -= 100#move up
            self.dir[0] = -self.dir[0]
            self.entity.dir[0] = self.dir[0]

class Wait(AI):#also called after landing, from states_maggot
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.count = kwarg['count']
        self.next_state = kwarg['next_state']

    def update(self):
        self.count -= self.entity.game_objects.game.dt
        if self.count < 0:
            self.enter_AI(self.next_state)
