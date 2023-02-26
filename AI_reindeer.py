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

    def do_nothing(self,duration = 50):
        self.entity.AI = Nothing(self.entity,duration)

    def finish_action(self):#when it state animation finishes
        pass

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self,input,duration = 100):
        if input == 'Aggro':
            new_AI = Aggro1(self.entity)
            new_AI.enter_AI()

class Chase(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Transform_walk')#this one is walking

    def update(self):
        super().update()
        if abs(self.player_distance[0]) < self.entity.attack_distance:
            self.enter_AI('Attack')
        elif self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1
        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1

class Nothing(AI):
    def __init__(self,entity,duration=100000):
        super().__init__(entity)
        self.duration = duration

    def update(self):
        self.duration -= 1
        if self.duration < 0:
            self.enter_AI('Chase')

class Attack(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Attack_pre')

    def finish_action(self):#when it finished attack, called when attack animation finished
        self.do_nothing(50)

class Jumping(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Jump_pre')

    def update(self):
        super().update()
        self.entity.currentstate.handle_input('Jump')
        if self.counter > 100:
            self.exit_AI()

        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1

    def finish_action(self):#when it finished attack, called when attack animation finished
        self.enter_AI('Jumping')

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

        elif self.player_distance[0] < -self.entity.attack_distance:
            self.entity.dir[0] = -1
            self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'stage2':
            new_AI = Aggro2(self.entity)
            new_AI.enter_AI()

class Aggro2(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Angry')

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
        elif input == 'jumping':
            new_AI = Jumping(self.entity)
            new_AI.enter_AI()

class Aggro3(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.currentstate.enter_state('Angry')

    def update(self):
        super().update()
        if self.player_distance[0] > self.entity.attack_distance:
            self.entity.dir[0] = 1

            if random.randint(0, 100)==100:
                self.entity.currentstate.handle_input('Dash')
            elif random.randint(0, 100)==99:
                self.entity.currentstate.handle_input('Special_attack')
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
            else:
                self.entity.currentstate.handle_input('Walk')
        else:
            self.entity.currentstate.handle_input('Idle')

    def handle_input(self,input,duration=100):
        if input == 'jumping':
            new_AI = Jumping(self.entity)
            new_AI.enter_AI()
