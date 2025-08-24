import random, sys

class WeatherStates():
    def __init__(self, entity):
        self.entity = entity

    def update(self, dt):
        pass

    def enter_state(self, newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate.capitalize())(self.entity)#make a class based on the name of the newstate: need to import sys

class Idle(WeatherStates):
    def __init__(self,entity):
        super().__init__(entity)        

class IdleWind(WeatherStates):
    def __init__(self,entity):
        super().__init__(entity)        

    def update(self, dt):
        rand = random.randint(0, 1000)
        if rand==0:
            self.enter_state('wind')

class Wind(WeatherStates):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.start_wind(velocity = [-2, 0.1], lifetime = 500)#can randomise a bit

    def update(self, dt):
        self.entity.lifetime -= dt
        if self.entity.lifetime < 0:
            self.entity.stop_wind()
            self.enter_state('idle')        