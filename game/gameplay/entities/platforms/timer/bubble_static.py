from engine.utils import read_files
from gameplay.entities.platforms.timer.base_timer import BaseTimer

class BubbleStatic(BaseTimer):#static bubble
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/timer/bubble/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.lifetime = prop.get('lifetime', 100)

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            self.game_objects.timer_manager.start_timer(self.lifetime, self.deactivate)
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

    def deactivate(self):#called when first timer runs out
        self.hitbox = [self.hitbox[0],self.hitbox[1],0,0]
        self.game_objects.timer_manager.start_timer(self.lifetime, self.activate)
        self.currentstate.handle_input('Transition_1')

    def activate(self):
        self.hitbox = self.rect.inflate(0,0)
        self.currentstate.handle_input('Transition_2')

#breakable
