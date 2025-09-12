from engine.system import animation
from gameplay.entities.states import states_basic

class Ability():#aila abilities
    def __init__(self,entity):
        self.entity = entity
        self.game_objects = entity.game_objects
        self.level = 1#upgrade pointer
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.animation.play('idle_1')

    def level_up(self):
        self.level += 1

    def activate(self,level):#for UI of Aila abilities
        self.animation.play('active_' + str(level))
        self.level = level

    def deactivate(self,level):#for UI of Aila abilities
        self.animation.play('idle_' + str(level))
        self.level = level

    def initiate(self):#called when using the ability
        pass

    def update(self, dt):#called from gameplayHUD
        self.animation.update(dt)
        self.currentstate.update(dt)

    def reset_timer(self):
        pass