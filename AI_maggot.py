import sys

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_AI(self,newAI, **kwarg):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input):
        pass

    def deactivate(self):#called when health < 0
        self.enter_AI('Idle')

    def update(self):
        pass

class Idle(AI):#initialised here
    def __init__(self,entity):
        super().__init__(entity)

class Run_away(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.run()
        self.turn_around()

    def run(self):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0]: return
        self.entity.patrol()

    def turn_around(self):
        if self.player_distance[0] >= 0 and self.entity.dir[0] == 1 or self.player_distance[0] < 0 and self.entity.dir[0] == -1:#e.g. player jumpt over entity
            self.enter_AI('Wait', count = 100, next_state = 'Turn_around')

class Wait(AI):#also called after landing, from states_maggot
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.count = kwarg['count']
        self.next_state = kwarg['next_state']

    def update(self):
        self.count -= self.entity.game_objects.game.dt
        if self.count < 0:
            self.enter_AI(self.next_state)

class Turn_around(AI):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.dir[0] = -self.entity.dir[0]

    def update(self):
        self.enter_AI('Run_away')
