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
        self.entity.currentstate.handle_input('Idle')

    def update(self):
        super().update()
        if abs(self.player_distance[0])<self.entity.aggro_distance:
            new_AI = Aggro1(self.entity)
            new_AI.enter_AI()

    def handle_input(self,input,duration = 100):
        if input == 'Aggro':
            new_AI = Aggro1(self.entity)
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

class Aggro1(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1
            self.entity.currentstate.handle_input('Walk')

        elif abs(self.player_distance[0]) < self.entity.attack_distance:
            self.entity.currentstate.handle_input('Attack')
            self.handle_input('Rest',duration=120)

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1
            self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'stage2':
            new_AI = Aggro2(self.entity)
            new_AI.enter_AI()
        elif input == 'Rest':
            new_AI = Pause(self.entity,duration)
            new_AI.enter_AI()

class Aggro2(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            else:
                self.entity.currentstate.handle_input('Walk')

        elif abs(self.player_distance[0])<self.entity.attack_distance:
            self.entity.currentstate.handle_input('Attack')
            self.handle_input('Rest',duration=120)

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            else:
                self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'stage3':
            new_AI = Aggro3(self.entity)
            new_AI.enter_AI()
        elif input == 'Rest':
            new_AI = Pause(self.entity,duration)
            new_AI.enter_AI()

class Aggro3(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            elif random.randint(0, 100)==99:
                self.entity.currentstate.handle_input('Special_attack')
                self.handle_input('Rest',duration=120)
            else:
                self.entity.currentstate.handle_input('Walk')

        elif abs(self.player_distance[0])<self.entity.attack_distance:
            self.entity.currentstate.handle_input('Attack')
            self.handle_input('Rest',duration=120)

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            elif random.randint(0, 100)==99:
                self.entity.currentstate.handle_input('Special_attack')
                self.handle_input('Rest',duration=120)
            else:
                self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'Rest':
            new_AI = Pause(self.entity,duration)
            new_AI.enter_AI()
