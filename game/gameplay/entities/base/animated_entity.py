from engine.system import animation

from gameplay.entities.base.static_entity import StaticEntity
from gameplay.entities.states import states_basic

class AnimatedEntity(StaticEntity):#animated stuff, i.e. cosmetics
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#

    def update(self, dt):
        self.currentstate.update(dt)
        self.animation.update(dt)    

    def reset_timer(self):#called from aniumation when the animation is finished
        self.currentstate.increase_phase()

    def release_texture(self):#called when .kill() and empty group
        for state in self.sprites.keys():
            for frame in range(0,len(self.sprites[state])):
                self.sprites[state][frame].release()