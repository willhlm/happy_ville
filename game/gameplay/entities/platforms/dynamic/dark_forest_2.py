from engine.system import animation
from engine.utils import read_files
from .base_dynamic import BaseDynamic
from . import states_moving_platform

class DarkForest_2(BaseDynamic):#dynamic one: #shoudl be added to platforms and dynamic_platforms groups
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/block/moving_platform/dark_forest_2/', game_objects)
        self.image = self.sprites['off'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.ID_key = prop.get('ID', None)

        self.animation = animation.Animation(self)
        self.currentstate = states_moving_platform.Off(self)#

    def update_vel(self, dt):
        pass
