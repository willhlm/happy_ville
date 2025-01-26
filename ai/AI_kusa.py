import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.counter = 0
        self.player_distance = [0,0]

    def enter_AI(self,newAI):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input,duration=100):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.counter += 1

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if abs(self.player_distance[0])<150:
            self.entity.currentstate.handle_input('Transform')
            self.enter_AI('Aggro1')

    def handle_input(self,input,duration = 100):
        if input == 'Aggro':
            self.enter_AI('Aggro1')
        elif input == 'Pause':
            self.entity.AI = Pause(self.entity,duration)

class Nothing(AI):
    def __init__(self,entity):
        super().__init__(entity)

class Pause(AI):#the entity should just stay and do nothing for a while
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.duration = duration

    def update(self):
        self.duration -= 1
        if self.duration < 0:
            self.enter_AI('Aggro1')

class Aggro1(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1
            self.entity.currentstate.handle_input('Walk')
        elif abs(self.player_distance[0]) < self.entity.attack_distance:

            if self.player_distance[0]>0:
                self.entity.dir[0]=1
            else:
                self.entity.dir[0]=-1

            self.entity.currentstate.handle_input('Attack')
            self.handle_input('Pause',duration=120)

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1
            self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

        if abs(self.player_distance[0])>self.entity.aggro_distance:
            pass#self.exit_AI()

    def handle_input(self,input,duration=100):
        if input == 'Pause':
            self.entity.AI = Pause(self.entity,duration)
