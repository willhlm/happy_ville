import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.counter = 0
        self.player_distance = [0,0]

    def enter_AI(self):
        self.entity.AI_stack.append(self)

    def exit_AI(self):
        self.entity.AI_stack.pop()

    def handle_input(self,input):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.counter += 1

    def set_AI(self,new_AI):
        self.entity.AI_stack.append(getattr(sys.modules[__name__], new_AI)(self.entity))#make a class based on the name of the newstate: need to import sys

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.direction='air'

    def update(self):#a betetr way to code it?
        super().update()
        if self.entity.collision_types['bottom']:
            self.direction='bottom'
            self.entity.currentstate.dir=[1,0]#animation direction

        elif self.entity.collision_types['left']:
            self.direction='left'
            self.entity.currentstate.dir=[0,-1]

        elif self.entity.collision_types['top']:
            self.direction='top'
            self.entity.currentstate.dir=[-1,0]

        elif self.entity.collision_types['right']:
            self.direction='right'
            self.entity.currentstate.dir=[0,1]

        if self.direction=='bottom' and not self.entity.collision_types['bottom']:#right side
            self.entity.acceleration=[-1,0]
            self.entity.dir=[0,-1]#walking direction

        elif self.direction=='left' and not self.entity.collision_types['left']:
            self.entity.acceleration=[0,-1]
            self.entity.dir=[-1,0]

        elif self.direction=='top' and not self.entity.collision_types['top']:
            self.entity.acceleration=[1,0]
            self.entity.dir=[0,1]

        elif self.direction=='right' and not self.entity.collision_types['right']:
            self.entity.acceleration=[0,1]
            self.entity.dir=[1,0]

    def handle_input(self,input,duration = 100):
        if input == 'Aggro':
            new_AI = Aggro1(self.entity)
            new_AI.enter_AI()
        elif input == 'Rest':
            new_AI = Pause(self.entity,duration)
            new_AI.enter_AI()

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
            self.exit_AI()#return to previous AI
