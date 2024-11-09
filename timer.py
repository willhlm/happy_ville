class Timer_manager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.timers = []  # List of active timers

    def start_timer(self, duration, callback, ID = None):
        timer = Timer(self, duration, callback, ID)
        self.timers.append(timer)
        return timer

    def remove_ID_timer(self, ID):
        self.timers = [timer for timer in self.timers if timer.ID != ID]

    def clear_timers(self):
        self.timers = []

    def remove_timer(self, timer):
        self.timers.remove(timer)        

    def update(self):
        for timer in self.timers[:]:  # Copy list for safe removal
            timer.update()

class Timer():
    def __init__(self, timer_manager, duration, callback, ID):
        self.timer_manager = timer_manager
        self.duration = duration
        self.callback = callback
        self.ID = ID

    def update(self):
        self.duration -= self.timer_manager.game_objects.game.dt#* self.entity.game_objects.player.slow_motion
        if self.duration < 0:
            self.callback()
            self.timer_manager.remove_timer(self)

