class Time_manager():#can append things in series
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.reset()

    def update(self, dt):
        self.current_modifier().update(dt)

    def modify_time(self, **kwarg):
        self.time_modifiers.append(Slow_motion(self.game_objects, **kwarg))
        self.refresh_time_scale()

    def reset(self):
        self.time_modifiers = [Idle()]
        self.time_scale = 1

    def current_modifier(self):
        return self.time_modifiers[-1]

    def refresh_time_scale(self):
        self.time_scale = self.current_modifier().time_scale

    def get_dt(self, dt):
        return dt * self.time_scale

class Idle():
    def __init__(self):
        self.time_scale = 1

    def expire(self):
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
        if self.lifetime <= 0:
            self.expire()

    def expire(self):
        time_manager = self.game_objects.time_manager
        if time_manager.time_modifiers and time_manager.current_modifier() is self:
            time_manager.time_modifiers.pop()
        time_manager.refresh_time_scale()
        if self.callback:
            self.callback()
