class Time_manager():#can append things in series
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.time_scale = 1
        self.reset()

    def update(self, dt):
        self.time_modifiers[-1].update(dt)        

    def modify_time(self, **kwarg):
        self.time_modifiers.append(Slow_motion(self.game_objects, **kwarg))

    def reset(self):
        self.time_modifiers = [Idle()]

    def set_time_scale(self, time_scale):
        self.time_scale = time_scale

class Idle():
    def __init__(self):   
        pass

    def update(self, dt):        
        pass  

class Slow_motion():
    def __init__(self, game_objects, **kwarg):   
        self.game_objects = game_objects
        self.time_scale = kwarg.get('time_scale', 0.5)
        self.lifetime = kwarg.get('duration', 100)
        self.callback = kwarg.get('callback', None)

    def update(self, dt):
        self.lifetime -= dt
        self.game_objects.time_manager.set_time_scale(self.time_scale)
        if self.lifetime <= 0:
            self.game_objects.time_manager.set_time_scale(1)
            self.game_objects.time_manager.time_modifiers.pop(-1)   
            if self.callback: self.callback()