class Status():#like timers, but there is an effect during update
    def __init__(self, entity, duration, callback = None):
        self.entity = entity
        self.duration = duration
        self.callback = callback
        self.active = False
        self.lifetime = 0

    def activate(self):#add timer to the entity timer list
        self.lifetime = self.duration
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self, dt):
        if not self.active:
            return

        self.lifetime -= dt
        if self.lifetime < 0:
            self.deactivate()
