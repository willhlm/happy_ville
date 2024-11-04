class Timer_manager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.timers = []  # List of active timers

    def start_timer(self, duration, callback, entity = None):
        timer = Timer(self, duration, callback, entity)
        self.timers.append(timer)

    def remove_entity_timers(self, entity):
        self.timers = [timer for timer in self.timers if timer.entity != entity]

    def clear_timers(self):
        self.timers = []

    def remove_timer(self, timer):
        self.timers.remove(timer)        

    def update(self):
        for timer in self.timers[:]:  # Copy list for safe removal
            timer.update()

class Timer():
    def __init__(self, timer_manager, duration, callback, entity):
        self.timer_manager = timer_manager
        self.duration = duration
        self.callback = callback
        self.entity = entity

    def update(self):
        self.duration -= self.timer_manager.game_objects.game.dt#* self.entity.game_objects.player.slow_motion
        if self.duration < 0:
            self.callback()
            self.timer_manager.remove_timer(self)

