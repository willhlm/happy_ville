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
        if not self.entity.configs:
            return
        rand = random.randint(0, 1000)
        if rand==0:
            self.enter_state('wind')

class Wind(WeatherStates):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.start_wind()#can randomise a bit

    def update(self, dt):
        expired_layers = []
        for layer_name in self.entity.active_wind.keys():
            self.entity.active_wind[layer_name]['lifetime'] -= dt
            if self.entity.active_wind[layer_name]['lifetime'] < 0:
                expired_layers.append(layer_name)

        for layer_name in expired_layers:
            self.entity.stop_wind(layer_name)

        if not self.entity.active_wind:
            self.enter_state('idle')        
