import constants as C

class Animation():
    def __init__(self, entity, **kwarg):
        self.entity = entity
        self.entity.slow_motion = 1#this value can be changed for player so that it counterasct teh slow motinos
        self.entity.state = 'idle'#default animation state
        self.framerate = kwarg.get('framerate', C.animation_framerate)
        self.frame = 0
        self.image_frame = 0#used for normal maps

    def reset_timer(self):
        self.frame = 0
        self.image_frame = 0

    def update(self):
        frame = int(self.frame)
        self.entity.image = self.entity.sprites[self.entity.state][frame]  
        self.image_frame = frame#save the current frame. Used for normal maps     
        self.frame += self.framerate * self.entity.game_objects.game.dt * self.entity.slow_motion

        if self.frame >= len(self.entity.sprites[self.entity.state]):
            self.entity.reset_timer()
            self.reset_timer()
