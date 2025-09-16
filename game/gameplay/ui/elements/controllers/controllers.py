from engine.system import animation
from . import states_buttons

class Controllers():
    def __init__(self, pos, game_objects,type):
        self.game_objects = game_objects#animation need it
        self.animation = animation.Animation(self)
        self.currentstate =  getattr(states_buttons, type.capitalize() + '_idle')(self)

    def reset_timer(self):#animation neeed it
        pass

    def update(self, dt):
        self.animation.update(dt)

