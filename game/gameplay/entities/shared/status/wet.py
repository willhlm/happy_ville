import random 
from gameplay.entities.shared.status.base.status import Status

class Wet(Status):#"a wet status". activates when player baths, and spawns particles that drops from player
    def __init__(self,entity, duration):
        super().__init__(entity, duration)
        self.spawn_frequency = 5#how often to spawn particle
        self.time = 0

    def activate(self, water_tint):#called when aila bathes (2D water)
        self.lifetime = self.duration#reset the duration
        self.water_tint = water_tint
        self.drop()
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.entity.timers.append(self)

    def update(self, dt):
        super().update(dt)
        self.time += dt
        if self.time > self.spawn_frequency:
            self.time = 0
            self.drop()

    def drop(self):
        pos = [self.entity.hitbox.centerx + random.randint(-5,5), self.entity.hitbox.centery + random.randint(-5,5)]
        c = [self.water_tint[0]*255, self.water_tint[1]*255, self.water_tint[2]*255, 255]
        self.entity.game_objects.particles.emit('drop', pos,  n=1, colour=c, gravity_scale=0.2)