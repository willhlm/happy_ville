import constants as C

class Animation():
    def __init__(self, entity):
        self.entity = entity
        self.entity.slow_motion = 1#this value can be changed for player so that it counterasct teh slow motinos
        self.entity.state = 'idle'#default animation state
        self.framerate = C.animation_framerate
        self.frame = 0

    def reset_timer(self):
        self.frame = 0

    def update(self):
        self.entity.image = self.entity.sprites[self.entity.state][int(self.frame)]
        self.frame += self.framerate * self.entity.game_objects.game.dt * self.entity.slow_motion

        if self.frame >= len(self.entity.sprites[self.entity.state]):
            self.entity.reset_timer()
            self.reset_timer()
