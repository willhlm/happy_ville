from engine.utils import read_files
from gameplay.entities.platforms.timer.base_timer import BaseTimer

class Nordveden_1(BaseTimer):#standing on it makes the platform crumble
    def __init__(self, pos, game_objects, ID):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/block/collision_time/nordveden_1/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.lifetime = 10
        self.ID = ID

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
        self.game_objects.world_state.state[self.game_objects.map.level_name]['breakable_platform'][self.ID] = True
        self.kill()
