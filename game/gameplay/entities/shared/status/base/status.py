class Status():#like timers, but there is an effect during update
    def __init__(self, entity, duration, callback = None):
        self.entity = entity
        self.duration = duration
        self.callback = callback

    def activate(self):#add timer to the entity timer list
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0:
            self.deactivate()