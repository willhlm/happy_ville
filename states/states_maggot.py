import sys, random
from states_entity import Entity_States

class BasicStates(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

class Idle(BasicStates):#initialised here
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Run_away')

class Run_away(BasicStates):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.animation.play('walk')

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.run()
        self.turn_around()

    def run(self):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0]: return
        self.entity.patrol()

    def turn_around(self):
        if self.player_distance[0] >= 0 and self.entity.dir[0] == 1 or self.player_distance[0] < 0 and self.entity.dir[0] == -1:#e.g. player jumpt over entity
            self.enter_state('Wait', count = 100, next_state = 'Turn_around')

class Wait(BasicStates):#also called after landing, from states_maggot
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.count = kwarg['count']
        self.next_state = kwarg['next_state']
        self.entity.animation.play('idle')

    def update(self):
        self.count -= self.entity.game_objects.game.dt
        if self.count < 0:
            self.enter_state(self.next_state)

class Turn_around(BasicStates):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.dir[0] = -self.entity.dir[0]
        self.entity.animation.play('idle')

    def update(self):
        self.enter_state('Run_away')
