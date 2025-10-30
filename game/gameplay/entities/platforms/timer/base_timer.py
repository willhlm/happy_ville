from engine.system import animation
from gameplay.entities.platforms.texture.base_texture import BaseTexture
from . import states_time_collision

class BaseTimer(BaseTexture):#collision block that dissapears if aila stands on it
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_time_collision.Idle(self)#

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):#called when aila lands on platoform
        if entity.velocity[1] < 0: return#going up
        offset = entity.velocity[1] + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            self.game_objects.timer_manager.start_timer(60, self.deactivate)
            entity.down_collision(self)
            entity.limit_y()
            entity.update_rect_y()
