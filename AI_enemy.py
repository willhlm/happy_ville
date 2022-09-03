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

    def handle_input(self,input,duration=100):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.counter += 1

    def set_AI(self,new_AI):
        self.entity.AI_stack.append(getattr(sys.modules[__name__], new_AI)(self.entity))#make a class based on the name of the newstate: need to import sys

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        rand=random.randint(0,1000)
        if rand>970:
            self.entity.currentstate.handle_input('Idle')
            #self.handle_input('Pause',duration=120)
            self.entity.dir[0] = -self.entity.dir[0]
        else:

            self.entity.currentstate.handle_input('Walk')
            #self.handle_input('Pause',duration=120)

        if abs(self.player_distance[0])<self.entity.aggro_distance:
            new_AI = Aggro1(self.entity)
            new_AI.enter_AI()

    def handle_input(self,input,duration = 100):
        if input == 'Aggro':
            new_AI = Aggro1(self.entity)
            new_AI.enter_AI()
        elif input == 'Pause':
            new_AI = Pause(self.entity,duration)
            new_AI.enter_AI()

class Nothing(AI):
    def __init__(self,entity):
        super().__init__(entity)

class Pause(AI):#the entity should just stay and do nothing for a while
    def __init__(self,entity,duration):
        super().__init__(entity)
        self.duration = duration
        self.entity.currentstate.handle_input('Idle')

    def update(self):
        self.duration -= 1
        if self.duration < 0:
            self.exit()#return to previous AI

    def exit(self):
        self.exit_AI()#return to previous AI

class Trun_around(Pause):#when the player jumps over, should be a delays before the entity turns around
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def exit(self):
        super().exit()
        self.entity.dir[0] = -self.entity.dir[0]

class Aggro1(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:

            if self.entity.dir[0] == -1:#turn around
                self.handle_input('Trun_around',duration=20)#short pause
            else:
                self.entity.currentstate.handle_input('Walk')

        elif abs(self.player_distance[0]) < self.entity.attack_distance:

            if self.player_distance[0]>0:
                self.entity.dir[0]=1
            else:
                self.entity.dir[0]=-1

            self.entity.currentstate.handle_input('Attack')
            self.handle_input('Pause',duration=120)

        elif self.player_distance[0] < -self.entity.attack_distance:

            if self.entity.dir[0] == 1:#turn aroud
                self.handle_input('Trun_around',duration=20)#short pause
            else:
                self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

        if abs(self.player_distance[0])>self.entity.aggro_distance:
            self.exit_AI()

    def handle_input(self,input,duration=100):
        if input == 'Pause':
            new_AI = Pause(self.entity,duration)
            new_AI.enter_AI()
        elif input == 'Trun_around':
            new_AI = Trun_around(self.entity,duration)
            new_AI.enter_AI()
