class Time_manager():#can append things in series
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.reset()

    def update(self):
        self.time_modifiers[-1].update()

    def modify_time(self, **kwarg):
        self.time_modifiers.append(Slow_motion(self.game_objects, **kwarg))

    def reset(self):
        self.time_modifiers = [Idle()]

class Idle():
    def __init__(self):   
        pass

    def update(self):
        pass 

class Slow_motion():
    def __init__(self, game_objects, **kwarg):   
        self.game_objects = game_objects
        self.time_scale = kwarg.get('time_scale', 0.5)
        self.lifetime = kwarg.get('duration', 100)

    def update(self):
        self.lifetime -= self.game_objects.game.dt
        self.game_objects.game.dt *= self.time_scale  
        if self.lifetime < 0:
            self.game_objects.time_manager.time_modifiers.remove(self)   