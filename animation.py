import constants as C

class Animation():
    def __init__(self, entity, **kwarg):
        self.entity = entity
        self.entity.slow_motion = 1#this value can be changed for player so that it counterasct teh slow motinos
        self.animation_name = kwarg.get('animation_name', 'idle')#default animation state
        self.framerate = kwarg.get('framerate', C.animation_framerate)
        self.frame = 0
        self.image_frame = 0#used for normal maps
        self.direction = kwarg.get('direction', 1)#1 or -1: animaion direction

    def reset_timer(self):
        self.frame = 0
        self.image_frame = 0

    def update(self):
        frame = int(self.frame)
        self.entity.image = self.entity.sprites[self.animation_name][frame]  
        self.image_frame = 0#frame#save the current frame. Used for normal maps     
        self.frame += self.framerate * self.entity.game_objects.game.dt * self.entity.slow_motion * self.direction

        if self.frame * self.direction >= len(self.entity.sprites[self.animation_name]):
            self.entity.reset_timer()
            self.reset_timer()

    def play(self, name):
        self.animation_name = name
        self.reset_timer()