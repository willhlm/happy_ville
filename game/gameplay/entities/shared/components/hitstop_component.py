class HitstopComponent():
    def __init__(self):
        self.time = 0
        self.scale = 0
        self.callbacks = []
    
    def start(self, duration, callback = None, scale = 0):
        self.time = max(self.time, duration)  # Can extend existing hitstop
        self.scale = scale
        self.callbacks = callback or []

    def update(self, dt):
        self.time -= dt
        if self.time <= 0:
            self._reset()

    def get_sim_dt(self, dt):
        """Returns scaled dt while hitstop is active, dt otherwise."""
        if self.time > 0: 
            return dt * self.scale
        return dt 

    def _reset(self):
        self.time = 0
        self.scale = 0
        for callback in self.callbacks:
            callback()
        self.callbacks.clear() 