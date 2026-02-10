class HitstopComponent():
    def __init__(self):
        self.time = 0
        self.callbacks = []
    
    def start(self, duration, callback = []):
        self.time = max(self.time, duration)  # Can extend existing hitstop
        self.callbacks = callback 

    def update(self, dt):
        self.time -= dt
        if self.time <= 0:
            for callback in self.callbacks:
                callback()
            self.callbacks.clear() 

    def get_sim_dt(self, dt):
        """Returns 0 when frozen, dt when active"""        
        if self.time > 0: 
            return 0
        return dt 