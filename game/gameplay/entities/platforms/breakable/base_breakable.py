from engine.system import animation
from engine.utils import read_files
from gameplay.entities.states import states_basic
from gameplay.entities.platforms.texture.base_texture import BaseTexture

class BaseBreakable(BaseTexture):#breakable collision blocks
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.flags = {'invincibility': False}
        self.health = 3
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#

    def dead(self):#called when death animatin finishes
        self.kill()

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def take_dmg(self, projectile):
        if self.flags['invincibility']: return
        self.health -= projectile.dmg
        self.flags['invincibility'] = True

        self.game_objects.camera_manager.camera_shake(amplitude = 3, duration = 10)

        if self.health > 0:#check if dead¨
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            #turn white TODO
        else:#if dead
            self.currentstate.enter_state('Death')#overrite any state and go to deat
