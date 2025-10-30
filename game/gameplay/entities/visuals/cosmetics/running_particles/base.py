from gameplay.entities.base.animated_entity import AnimatedEntity

class RunningParticles(AnimatedEntity):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def reset_timer(self):
        self.kill()

    def release_texture(self):#stuff that have pool shuold call this
        pass

